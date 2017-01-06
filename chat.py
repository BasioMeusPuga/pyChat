#!/usr/bin/python

import random
import socket
import crypt
import threading
import time


hostname = socket.gethostname()
serverport = int(input('Server port: '))
clientport = int(input('Client port: '))


class Colors:
	CYAN = '\033[96m'
	YELLOW = '\033[93m'
	GREEN = '\033[92m'
	RED = '\033[91m'
	WHITE = '\033[97m'
	ENDC = '\033[0m'


class Server:
	def __init__(self, serverport):
		self.messages = []
		self.serverport = serverport

	def do_the_serving(self):
		s = socket.socket()
		s.bind((hostname, self.serverport))
		s.listen(1)

		while True:
			client_object = s.accept()[0]
			if self.messages:
				for i in self.messages:
					client_object.send(str.encode(i))
				self.messages.clear()
			client_object.close()

	def chat_input(self):
		message = input('> ')
		if message:
			self.messages.append(message)
		self.chat_input()


class Client:
	def __init__(self, clientport):
		self.messages = []
		self.clientport = clientport

	def check_messages(self):
		s = socket.socket()
		try:
			s.connect((hostname, self.clientport))
			response = s.recv(1024).decode()
			if response != '':
				print(Colors.WHITE + response + Colors.ENDC)
			s.close()
		except ConnectionRefusedError:
			pass
		time.sleep(1)
		self.check_messages()


thisServer = Server(serverport)
thisClient = Client(clientport)


if __name__ == '__main__':
	threading.Thread(target=thisServer.do_the_serving).start()
	threading.Thread(target=thisServer.chat_input).start()
	threading.Thread(target=thisClient.check_messages).start()