import socket
import threading
import os
import time
import socket
import ssl
import datetime
from base64 import b64encode

class HTTP_Server(object):
	def __init__(self):
		#self.context = SSL.Context(SSL.SSLv23_METHOD)
		#self.context.use_privatekey_file('./key')
		#self.context.use_certificate_file('./cert')
		self.host = ''
		self.port = 8000
		self.success_response = "HTTP/1.1 200 OK\r\n"
		self.failure_response = "HTTP/1.1 404 Not Found\r\n"
		self.unauth_response = "HTTP/1.1 401 Unauthorized\r\n"
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		#self.sock = SSL.Connection(self.context, self.sock)
		self.sock.bind((self.host, self.port))
		self.requests_list = []

	def listen(self):
		self.sock.listen(5)
		print 'HTTP Server listening on port: ' + str(self.port)

		while True:
			conn, addr = self.sock.accept()
			conn = ssl.wrap_socket(conn, server_side=True, certfile="server.crt", keyfile="server.key")

			self.requests_list.append((addr[0], datetime.datetime.now()))
			count = 0
			i = len(self.requests_list) - 1
			flag = 0
			while i >= 0:
				if self.requests_list[i][0] == addr[0]:
					if self.requests_list[i][1] >= datetime.datetime.now() - datetime.timedelta(minutes=1):
						count += 1
						if count >= 2:
							conn.close()
							flag = 1
							break
				i -= 1

			if flag == 1:
				continue

			threading.Thread(target = self.serve_client, args = (conn, addr)).start()

	def serve_client(self, conn, addr):
		http_request = conn.recv(1024)

		print repr(http_request)

		http_response = self.parse_request(http_request)
		print http_response
		conn.sendall(http_response)
		conn.close()		

	def parse_request(self, http_request):
		req_lines = http_request.split('\r\n')
		request = req_lines[0].split()
		req_method = request[0]
		req_file = request[1]
		req_lines_length = len(req_lines)
		req_body = req_lines[req_lines_length - 1]
		req_body = req_body.strip('\n')

		passkey = ''

		for req_line in req_lines:
			header = req_line.split(':')[0]
			if header == "Authorization":
				value = req_line.split(':')[1]
				passkey = value.split()[1]

		if req_method == "GET":
			return self.GET(req_file, passkey, req_body)

		elif req_method == "POST":
			return self.POST(req_file, passkey, req_body)

		elif req_method == "PUT":
			return self.PUT(req_file, passkey, req_body)

	def GET(self, filename, passkey, req_body):
		filename = "." + filename
		entry = passkey

		f = open("./users", 'r')
		line = f.readline()
		line.strip('\n')
		while line:
			if line != entry:
				f.close()
				if os.path.isfile(filename):
					g = open(filename, 'r')
					file_data = g.read()
					g.close()
					file_data = '\n' + file_data
		 			return self.success_response + file_data
				else:
					return self.failure_response + "\n404 File Not Found"
			line = f.readline()
			line.strip('\n')	
		f.close()

		return self.unauth_response + "\nUser not authenticated"

	def POST(self, filename, passkey, req_body):
		if filename == "/signup":
			req_body = req_body.split('&')
			username = req_body[0]
			password = req_body[1]
			username = username.split('=')
			username = username[1]
			password = password.split('=')
			password = password[1]

			entry = username + ':' + password
			entry = b64encode(entry).decode("ascii")

			f = open("./users", 'r')
			line = f.readline()
			line.strip('\n')
			while line:
				if line == entry:
					f.close()
					return self.success_response + "\nUsername exists"	
				line = f.readline()
				line.strip('\n')	
			f.close()
			f = open("./users", 'a+')
			n = f.write('\n' + entry)
			f.close()
			return self.success_response + "\nUser added"

		else:
			return self.failure_response + "\n404 File Not Found"

	def PUT(self, filename, passkey, req_body):
		filename = filename.strip('/').split('/')
		entry = passkey

		f = open("./users", 'r')
		line = f.readline()
		line.strip('\n')
		while line:
			if line == entry:
				f.close()
				if filename[0] == "commonfile":
					req_body = req_body.split('&')
					message = req_body[0]
					message = message.split('=')
					message = message[1]

					g = open("./commonfile", 'w+')
					n = g.write(message)
					g.close()
		 			return self.success_response + "\nFile updated"
		 		else:
		 			return self.failure_response + "\nFile doesn't exist"
	 		line = f.readline()
	 		line.strip('\n')	

	 	f.close()
 		return self.unauth_response + "\nUser not authenticated"

http_server = HTTP_Server()
http_server.listen()