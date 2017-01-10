#!/usr/bin/python3

""" TO DO
Encryption
Build message buffer in case of disconnect
"""

import os
import sys
import time
import socket
import random
import pickle
import threading

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
	lastUpdate = time.time()


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
		form.move_cursor_to_bottom()
		# Color own name green
		form.chatDisplay.insertHtml(
			"<html><font color='green'><b>{0}</b></font>{1}</html>"
				.format(Options.nickname + ': ', self.chatInput.text()))
		form.chatDisplay.insertPlainText('\n')
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
			Options.nickname = self.settingsNick.text()
			Options.hostname = self.settingsServer.text().split(':')[0]
			Options.clientport = int(self.settingsServer.text().split(':')[1])
			self.hide()
		except:
			pass

	def go_back(self):
		self.hide()


def parse_response(response):
	# display list of online clients
	online_clients = response['online_clients']
	form.chatClients.clear()
	form.chatClients.addItems(online_clients)

	if response['message'] is not None:
		form.move_cursor_to_bottom()
		for i in response['message']:
			form.chatDisplay.insertHtml("<html><b>{0}</b>{1}</html>".format(i[1] + ": ", i[2]))
			form.chatDisplay.insertPlainText('\n')
			form.move_cursor_to_bottom()

		# set lastUpdate according to the last message received by the client
		State.lastUpdate = float(response['message'][-1][0])


def check_messages():
	while True:
		handshake = {
			'type': 'Handshake',
			'time': State.lastUpdate,
			'sender': Options.nickname
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


def send_message(message_string):
	# connected to the sendtext function of the ChatUI class
	if message_string == '/quit' or message_string == '/exit':
		os._exit(0)

	chat_message = {
		'type': 'ChatMessage',
		'message': [time.time(), Options.nickname, message_string]
	}

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
