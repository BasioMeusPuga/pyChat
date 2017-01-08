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

from PyQt5 import QtWidgets
sys.path.insert(0, 'resources')
import clientinterface


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

		# event definitions
		self.chatInput.returnPressed.connect(self.sendtext)
		self.chatSend.clicked.connect(self.sendtext)
		self.chatInput.setFocus()

	def sendtext(self):
		# Color own name green
		form.chatDisplay.insertHtml(
			"<html><font color='green'><b>{0}</b></font>{1}</html>"
				.format(Options.nickname + ': ', self.chatInput.text()))
		form.chatDisplay.insertPlainText('\n')
		send_message(self.chatInput.text())
		self.chatInput.clear()


def parse_response(response):
	State.lastUpdate = response['time']

	# display list of online clients
	online_clients = response['online_clients']
	form.chatClients.clear()
	form.chatClients.addItems(online_clients)

	if response['message'] is not None:
		form.chatDisplay.insertHtml(
			"<html><b>{0}</b>{1}</html>"
				.format(response['message'][1] + ": ", response['message'][2]))
		form.chatDisplay.insertPlainText('\n')


def check_messages():
	handshake = {
		'type': 'Handshake',
		'time': State.lastUpdate,
		'sender': Options.nickname
	}
	handshake_message = pickle.dumps(handshake)

	s = socket.socket()
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
	except (ConnectionRefusedError, ConnectionResetError):
		form.statusbar.showMessage('Not connected to server')

	time.sleep(1)
	check_messages()


def send_message(message_string):
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


def main():
	global form
	app = QtWidgets.QApplication(sys.argv)
	form = ChatUI()
	form.show()
	app.exec_()


if __name__ == '__main__':
	threading.Thread(target=main).start()
	time.sleep(1)
	# daemonizing the worker thread ensures it exits when the main (UI) thread does
	threading.Thread(target=check_messages, daemon=True).start()
