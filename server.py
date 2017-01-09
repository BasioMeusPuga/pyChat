#!/usr/bin/python3

""" TO DO
Send n older messages to a new client
"""

import time
import pickle
import socket
import sqlite3
import os.path
import threading


class Options:
	# Everything else seems to fail in case /etc/hosts points localhost to 127.0.0.1
	hostname = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
	serverport = 11011
	remember_for = 4


class State:
	online_clients = {}


dbPath = os.path.dirname(os.path.realpath(__file__)) + '/chat.db'
if not os.path.exists(dbPath):
	print('First run. Creating db and exiting.')
	database = sqlite3.connect(dbPath)
	database.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, TimeSent REAL, Sender TEXT, MessageText TEXT)")
	exit()


def client_check():
	client_iter = dict(State.online_clients)  # The dict() is required, idiot.
	State.online_clients.clear()

	for i in client_iter.keys():
		client_iter[i] += 1
		if client_iter[i] < Options.remember_for:  # Number of absent pings the server will remember a client for
			State.online_clients[i] = client_iter[i]

	time.sleep(1)
	client_check()


def parse_response(response):
	database = sqlite3.connect(dbPath)
	response = pickle.loads(response)

	if response['type'] == 'Handshake':
		client_lastupdate = response['time']
		client_name = response['sender']
		State.online_clients[client_name] = 0

		# this does not try to send ALL messages on first connect
		new_messages = database.execute("SELECT * FROM messages WHERE TimeSent > '{0}' AND Sender != '{1}'"
										.format(client_lastupdate, client_name)).fetchall()
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
			'online_clients': State.online_clients,
			'message': message
		}

		# return the last message(s) in the database in case the client's last update was before they arrived
		return pickle.dumps(server_response)

	elif response['type'] == 'ChatMessage':
		# put the incoming message in the database
		message_time = response['message'][0]
		message_sender = response['message'][1]
		message_text = response['message'][2].replace('\'', '\'\'')
		database.execute("INSERT INTO messages (TimeSent, Sender, MessageText) VALUES ('{0}', '{1}', '{2}')"
						 .format(message_time, message_sender, message_text))
		database.commit()
		return None


def main():
	s = socket.socket()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((Options.hostname, Options.serverport))
	print('\n' + 'Server running @ {0}:{1}'.format(Options.hostname, Options.serverport))
	s.listen(1)

	while True:
		client_object, client_addr = s.accept()
		incoming = client_object.recv(1024)

		server_response = parse_response(incoming)
		if server_response is not None:
			client_object.send(server_response)

		client_object.close()


def inputprompt():
	a = input('l / q / s > ')
	if a == 'q':
		database = sqlite3.connect(dbPath)
		database.execute("DELETE FROM messages")
		database.commit()
		database.close()
		os._exit(0)
	elif a == 'l':
		database = sqlite3.connect(dbPath)
		all_messages = database.execute("SELECT TimeSent, Sender, MessageText FROM messages").fetchall()
		if all_messages:
			for i in all_messages:
				time_sent = time.ctime(i[0])
				print('(' + time_sent + ') ' + i[1] + ': ' + i[2])
		else:
			print('Nothing yet')
		inputprompt()
	elif a == 's':
		for i in State.online_clients:
			print(i)
		inputprompt()
	else:
		inputprompt()


if __name__ == '__main__':
	threading.Thread(target=main).start()
	threading.Thread(target=client_check, daemon=True).start()
	threading.Thread(target=inputprompt).start()
