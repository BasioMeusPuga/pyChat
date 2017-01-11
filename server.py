#!/usr/bin/python3

import time
import pickle
import socket
import sqlite3
import os.path
import threading


class Options:
	# everything else seems to fail in case /etc/hosts points localhost to 127.0.0.1
	hostname = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
	serverport = 11011
	rememberFor = 3


class State:
	onlineClients = {}


dbPath = os.path.dirname(os.path.realpath(__file__)) + '/chat.db'
if not os.path.exists(dbPath):
	print('First run. Creating db and exiting.')
	database = sqlite3.connect(dbPath)
	# MessageText is BLOB because the server will only receive encrypted bytestream data
	database.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, TimeSent REAL, Sender TEXT, MessageText BLOB)")
	exit()


def client_check():
	while True:
		# the dict() is required, idiot.
		# because plz you want to emulate favorite celebrity not literally *become* them
		client_iter = dict(State.onlineClients)
		State.onlineClients.clear()

		for i in client_iter.keys():
			client_iter[i][0] += 1
			if client_iter[i][0] < Options.rememberFor:  # Number of absent pings the server will remember a client for
				State.onlineClients[i] = client_iter[i]
		time.sleep(1)


def parse_response(response):
	database = sqlite3.connect(dbPath)
	response = pickle.loads(response)

	if response['type'] == 'NickChange':
		old_nick = response['old_nick']
		new_nick = response['new_nick']

		State.onlineClients[new_nick] = State.onlineClients[old_nick]
		State.onlineClients.pop(old_nick)
		return None

	elif response['type'] == 'Handshake':
		client_name = response['sender']
		client_lastupdate = response['time']
		client_publickey = response['publickey']
		# the first element is 0 because it resets the "forget me" counter on each new ping
		State.onlineClients[client_name] = [0, client_publickey]

		# new messages are sent according to the last stated update time.
		# I've no idea how this works across timezones.
		new_messages = database.execute("SELECT * FROM messages WHERE TimeSent > '{0}' AND Sender != '{1}'"
										.format(client_lastupdate, client_name)).fetchall()

		# when in doubt, return None
		if new_messages:
			messages = []
			for i in new_messages:
				try:
					message_time = i[1]
					message_sender = i[2]
					message_text = pickle.loads(i[3])

					message_text_this_recipient = message_text[client_name]
					messages.append((message_time, message_sender, message_text_this_recipient))
				except KeyError:
					messages = None
		else:
			messages = None

		server_response = {
			'type': 'ChatMessage',
			'online_clients': State.onlineClients,
			'message': messages
		}
		return pickle.dumps(server_response)

	elif response['type'] == 'ChatMessage':
		# put the incoming message in the database
		message_time = response['time']
		message_sender = response['sender']

		# message_text is being pickled again because how do I even unknown length dictionary into a row?
		message_text = pickle.dumps(response['message'])
		database.execute("INSERT INTO messages (TimeSent, Sender, MessageText) VALUES (?, ?, ?)",
						 (message_time, message_sender, message_text))
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
		incoming = client_object.recv(2048)

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

		# commented out due to issue 28518 in python 3.6
		# database.execute("VACUUM")

		database.close()
		os._exit(0)

	elif a == 'l':
		database = sqlite3.connect(dbPath)
		all_messages = database.execute("SELECT TimeSent, Sender FROM messages").fetchall()
		if all_messages:
			for i in all_messages:
				time_sent = time.ctime(i[0])
				print(time_sent + ': ' + i[1])
		else:
			print('Nothing yet')
		inputprompt()

	elif a == 's':
		for i in State.onlineClients:
			print(i)
		inputprompt()

	else:
		inputprompt()


if __name__ == '__main__':
	threading.Thread(target=main).start()
	threading.Thread(target=client_check, daemon=True).start()
	time.sleep(1)
	threading.Thread(target=inputprompt).start()
