#!/usr/bin/python

import socket
import sqlite3
import os.path
import time
import pickle


dbPath = os.path.dirname(os.path.realpath(__file__)) + '/chat.db'
if not os.path.exists(dbPath):
	print('First run. Creating db and exiting.')
	database = sqlite3.connect(dbPath)
	database.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, TimeSent REAL, Sender TEXT, MessageText TEXT)")
	exit()

database = sqlite3.connect(dbPath)
hostname = socket.gethostname()
# serverport = input('Serverport: ')
serverport = 11011


def parse_response(response):
	response = pickle.loads(response)

	if response['type'] == 'Handshake':
		client_lastupdate = response['time']
		client_name = response['sender']

		# this does not try to send ALL messages on first connect
		new_messages = database.execute("SELECT * FROM messages WHERE TimeSent > '{0}' AND Sender != '{1}'".format(client_lastupdate, client_name)).fetchall()
		if new_messages:
			message_time = new_messages[0][1]
			message_sender = new_messages[0][2]
			message_text = new_messages[0][3]
			message = (message_time, message_sender, message_text)
		else:
			message = None

		server_response = {
			'type': 'ChatMessage',
			'time': time.time(),
			'message': message
		}

		# return the last message(s) in the database in case the client's last update was before they arrived
		return pickle.dumps(server_response)

	elif response['type'] == 'ChatMessage':
		# put the incoming message in the database
		message_time = response['message'][0]
		message_sender = response['message'][1]
		message_text = response['message'][2].replace('\'', '\'\'')
		database.execute("INSERT INTO messages (TimeSent, Sender, MessageText) VALUES ('{0}', '{1}', '{2}')".format(message_time, message_sender, message_text))
		database.commit()
		return None


def main():
	s = socket.socket()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((hostname, serverport))
	s.listen(1)

	while True:
		client_object, client_addr = s.accept()
		response = client_object.recv(1024)

		server_response = parse_response(response)
		if server_response is not None:
			client_object.send(server_response)

		client_object.close()

try:
	main()
except KeyboardInterrupt:
	database.execute("DELETE FROM messages")
	database.commit()
	exit()