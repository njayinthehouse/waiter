import socket
import threading
import os
import time
import socket
from OpenSSL import SSL

class HTTP_Server(object):
	def __init__(self):
		self.context = SSL.Context(SSL.SSLv23_METHOD)
		self.context.use_privatekey_file('./key')
		self.context.use_certificate_file('./cert')
		self.host = ''
		self.port = 8000
		self.success_response = "HTTP/1.1 200 OK\r\n"
		self.failure_response = "HTTP/1.1 404 Not Found\r\n"
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock = SSL.Connection(self.context, self.sock)
		self.sock.bind((self.host, self.port))

	def listen(self):
		self.sock.listen(5)
		print 'HTTP Server listening on port: ' + str(self.port)

		while True:
		    conn, addr = self.sock.accept()
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
		req_file = "." + req_file

		if req_method == "GET":
			return self.GET(req_file)

	def GET(self, filename):
		if os.path.isfile(filename):
			f = open(filename, 'r')
			file_data = f.read()
			file_data = '\n' + file_data
 			return self.success_response + file_data
		else:
			return self.failure_response + "\n404 File Not Found"

http_server = HTTP_Server()
http_server.listen()