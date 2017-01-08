#!/usr/bin/python

import socket
import threading
import time
import pickle
import random
import os

hostname = socket.gethostname()
clientport = 11011


class Colors:
	CYAN = '\033[96m'
	YELLOW = '\033[93m'
	GREEN = '\033[92m'
	RED = '\033[91m'
	WHITE = '\033[97m'
	ENDC = '\033[0m'


class State:
	nickname = ''
	for i in range(5):
		nickname += chr(random.randrange(97, 113))
	print('You are registered as ' + nickname)
	lastUpdate = time.time()


def parse_response(response):
	State.lastUpdate = response['time']
	if response['message'] is not None:
	 	print(response['message'])


def check_messages():
	handshake = {
		'type': 'Handshake',
		'time': State.lastUpdate,
		'sender': State.nickname
	}
	handshake_message = pickle.dumps(handshake)

	s = socket.socket()
	try:
		s.connect((hostname, clientport))
		s.send(handshake_message)

		try:
			response = pickle.loads(s.recv(1024))
			parse_response(response)
		except EOFError:
			pass

		s.close()
	except ConnectionRefusedError:
		pass

	# figure out how to terminate this gracefully in case of a KeyboardInterrupt
	time.sleep(1)
	check_messages()


def send_message():
	message_string = input('> ')
	if message_string == '/quit' or message_string == '/exit':
		os._exit(0)

	chat_message = {
		'type': 'ChatMessage',
		'message': [time.time(), State.nickname, message_string]
	}

	s = socket.socket()
	try:
		s.connect((hostname, clientport))
		s.send(pickle.dumps(chat_message))
		s.close()
	except ConnectionRefusedError:
		# try building a buffer of unsent messages
		pass

	send_message()


if __name__ == '__main__':
	threading.Thread(target=check_messages).start()
	threading.Thread(target=send_message).start()