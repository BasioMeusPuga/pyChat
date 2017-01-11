#!/usr/bin/python3

""" TO DO
Change keys after n handshakes
"""

import os
import sys
import time
import socket
import random
import pickle
import threading
import libnacl.public

# gui imports - sys.path.insert allows shifting of modules away from the root directory
from PyQt5 import QtWidgets, QtGui
sys.path.insert(0, 'resources')
import clientinterface
import settingsinterface


class Options:
	nickname = ''
	if nickname == '':
		for i in range(5):
			nickname += chr(random.randrange(97, 113))

	hostname = socket.gethostname()
	clientport = 11011


class State:
	serverConnected = False
	# because of end-to-end encryption, there's really no point in trying to fetch older messages from the server
	lastUpdate = time.time()
	onlineClients = None


class Encryption:
	def __init__(self):
		self.keypair = None
		self.publickey = None
		self.secretkey = None

	def generate_keypair(self):
		self.keypair = libnacl.public.SecretKey()
		self.publickey = self.keypair.pk
		self.secretkey = self.keypair.sk

	def generate_ciphertext(self, otherdudespublickey, plain_text):
		myBox = libnacl.public.Box(self.secretkey, otherdudespublickey)
		cipher_text = myBox.encrypt(plain_text)
		return cipher_text

	def generate_plaintext(self, otherdudespublickey, cipher_text):
		myBox = libnacl.public.Box(self.secretkey, otherdudespublickey)
		plain_text = myBox.decrypt(cipher_text)
		return plain_text.decode()


class ChatUI(QtWidgets.QMainWindow, clientinterface.Ui_MainWindow):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.setupUi(self)

		# toolbar
		settings_icon = QtGui.QIcon('resources/settings.png')
		exit_icon = QtGui.QIcon('resources/exit.png')
		self.toolBar.addAction(settings_icon, 'Settings', self.show_settings)
		self.toolBar.addAction(exit_icon, 'Exit', self.endthis)

		# chat display
		self.chatDisplay.ensureCursorVisible()

		# event definitions
		self.chatInput.returnPressed.connect(self.sendtext)
		self.chatSend.clicked.connect(self.sendtext)
		self.chatInput.setFocus()

	def endthis(self):
		os._exit(0)

	def move_cursor_to_bottom(self):
		# move the invisible cursor to the bottom after each addition
		self.chatDisplay.moveCursor(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)

	def show_settings(self):
		# the settings dialog is setModal(True) so disabling the main window isn't required
		settings.show()

	def sendtext(self):
		self.move_cursor_to_bottom()
		# color own name green
		self.chatDisplay.insertHtml(
			"<html><font color='green'><b>{0}</b></font>{1}</html>"
				.format(Options.nickname + ': ', self.chatInput.text()))
		self.chatDisplay.insertPlainText('\n')
		send_message(self.chatInput.text())
		self.chatInput.clear()


class SettingsUI(QtWidgets.QDialog, settingsinterface.Ui_chatSettings):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.setupUi(self)

		self.settingsNick.setText(Options.nickname)
		self.settingsServer.setText(Options.hostname + ':' + str(Options.clientport))

		self.settingsOC.accepted.connect(self.new_settings)
		self.settingsOC.rejected.connect(self.go_back)

	def new_settings(self):
		try:
			old_nick = str(Options.nickname)
			Options.nickname = self.settingsNick.text()
			if old_nick != Options.nickname:
				change_nick(old_nick, Options.nickname)

			Options.hostname = self.settingsServer.text().split(':')[0]
			Options.clientport = int(self.settingsServer.text().split(':')[1])
			self.hide()
		except:
			pass

	def go_back(self):
		self.hide()


def parse_response(response):
	# display list of online clients
	try:
		current_clients = dict(State.onlineClients)
	except TypeError:
		current_clients = {}
	State.onlineClients = response['online_clients']
	new_clients = [client_new for client_new in State.onlineClients.keys() if client_new not in [clients for clients in current_clients.keys()] and client_new != Options.nickname]
	clients_bgone = [clients for clients in current_clients.keys() if clients not in [client_new for client_new in State.onlineClients.keys()]]

	form.chatClients.clear()
	form.chatClients.addItems(State.onlineClients)

	if new_clients:
		for i in new_clients:
			form.move_cursor_to_bottom()
			form.chatDisplay.insertHtml("<html><font color='gray'><i>{0}</i><font></html>".format(i + ' appears. Out of friggin\' nowhere.'))
			form.chatDisplay.insertPlainText('\n')

	if clients_bgone:
		for i in clients_bgone:
			form.move_cursor_to_bottom()
			form.chatDisplay.insertHtml("<html><font color='gray'><i>{0}</i><font></html>".format(i + ' hath abandoned thee in thy hour of need.'))
			form.chatDisplay.insertPlainText('\n')

	if response['message'] is not None:
		for i in response['message']:
			message_sender = i[1]
			message_sender_publickey = State.onlineClients[message_sender][1]
			message_ciphertext = i[2]
			message_plaintext = encrypt.generate_plaintext(message_sender_publickey, message_ciphertext)

			form.move_cursor_to_bottom()
			form.chatDisplay.insertHtml("<html><b>{0}</b>{1}</html>".format(message_sender + ": ", message_plaintext))
			form.chatDisplay.insertPlainText('\n')

		# set lastUpdate according to the last message received by the client
		State.lastUpdate = float(response['message'][-1][0])


def check_messages():
	handshakes_sent = 0
	while True:
		# regenerate keys every 25 handshakes (or 5 seconds) - not working
		handshakes_sent += 1
		if handshakes_sent >= 5:
			# encrypt.generate_keypair()
			handshakes_sent = 0

		handshake = {
			'type': 'Handshake',
			'sender': Options.nickname,
			'time': State.lastUpdate,
			'publickey': encrypt.publickey
		}
		handshake_message = pickle.dumps(handshake)

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.connect((Options.hostname, Options.clientport))
			s.send(handshake_message)

			try:
				response = pickle.loads(s.recv(2048))
				parse_response(response)
			except EOFError:
				pass

			form.statusbar.showMessage('Registered as ' + Options.nickname)
			s.close()

		except (ConnectionRefusedError, ConnectionResetError, OSError):
			form.statusbar.showMessage('Not connected to server')
			form.chatClients.clear()

		# this basically decides the polling interval
		time.sleep(.2)


def change_nick(old_nick, new_nick):
	chat_message = {
		'type': 'NickChange',
		'old_nick': old_nick,
		'new_nick' : new_nick
	}
	one_way_send(chat_message)


# connected to the sendtext function of the ChatUI class
def send_message(message_string):
	if message_string == '/quit' or message_string == '/exit':
		os._exit(0)

	cipher_text = {}
	for i in State.onlineClients.keys():
		if i != Options.nickname:
			cipher_text[i] = encrypt.generate_ciphertext(State.onlineClients[i][1], str.encode(message_string))

	chat_message = {
		'type': 'ChatMessage',
		'time': time.time(),
		'sender': Options.nickname,
		'message': cipher_text
	}
	one_way_send(chat_message)


# distinct from the handshake because it doesn't expect a reply
def one_way_send(chat_message):
	s = socket.socket()
	try:
		s.connect((Options.hostname, Options.clientport))
		s.send(pickle.dumps(chat_message))
		s.close()
		form.statusbar.showMessage('Registered as ' + Options.nickname)
	except (ConnectionRefusedError, ConnectionResetError):
		form.statusbar.showMessage('Not connected to server')
		form.chatClients.clear()


def main():
	# initialize encryption
	global encrypt
	encrypt = Encryption()
	encrypt.generate_keypair()

	# initialize the gui
	global form, settings
	app = QtWidgets.QApplication(sys.argv)
	form = ChatUI()
	settings = SettingsUI()
	form.show()
	app.exec_()


if __name__ == '__main__':
	threading.Thread(target=main).start()
	time.sleep(1)
	# daemonizing the worker thread ensures it exits when the main (UI) thread does
	threading.Thread(target=check_messages, daemon=True).start()
