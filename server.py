import sys
import socket
import os
import struct


class Server:
	next_node = {'address': "", "port": 0, "hash_code": ""}
	hash_code = 0
	address = ""
	port = 0
	dir_path = ""
	buf_size = 1024

	def __init__(self, address, port):
		self.address = address
		self.port = port
		self.dir_path = address + '-' + str(port)
		if (os.path.isdir(self.dir_path) == False):
			os.mkdir(self.dir_path)

	def connect(self, address, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((address, port))
		return sock

	def show_next(self, first_node):
		if (first_node == self.next_node['address'] + ":" + str(self.next_node['port'])):
			return ""
		sock = connect(address, port)
		sock.send('show,' + first_node)
		ret = sock.recv(self.buf_size)
		sock.close()
		return ret

	def find(self, address, port, sha1_value):
		sock = connect(address, port)
		sock.send('find,', address + ',' + port)
		sock.recv(self.buf_size)
		sock.close()

	def transfer_file(sefl, address, port, file_path):
		sock = connect(address, port)

	def send_file(address, port, file_path):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((address, port))

		sock.send('file,' + file_path)
		buf = ""
		while (buf != 'begin'):
			buf = sock.recv(5)
		buf_size = 1024
		if (buf == 'begin'):
			sock.send(struct.pack("i", os.stat(file_path).st_size))
			fp = open(file_path, "rb")
			while True:
				data = fp.read(buf_size)
				if (not data): 
					break
				sock.send(data)
			fp.close()
		sock.close()

	def receive_file(self, connection, file_path):
		buf = connection.recv(struct.calcsize("i"))
		#unpack return a tuple
		file_size = struct.unpack("i", buf)[0]
		print 'file size:', file_size
		fp = open(self.dir_path + '/' + file_path, "wb")
		while file_size > 0:
			if (file_size < self.buf_size):
				buf = connection.recv(file_size)
			else:
				buf = connection.recv(self.buf_size)
			fp.write(buf)
			file_size = file_size - self.buf_size
		fp.close()

	def run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((self.address, self.port))
		print self.address, self.port
		sock.listen(5)
		while True:
			connection, address = sock.accept()
			buf = connection.recv(self.buf_size)
			s = buf.split(',')
			print 'command', s[0]
			if (s[0] == 'transfer'):
				self.transfer_file(s[1], s[2], s[3])
			elif (s[0] == 'find'):
				print s[1], s[2], s[3]
				self.find(s[1], s[2], s[3])
			elif (s[0] == 'show'):
				res = self.address + ':' + self.port + '\n'
				if (len(s) > 1):
					self.show_next(self.address, s[1])
				else:
					self.show_next(self.address, self.address + ":" + str(self.port))
				connection.send(res)
			elif (s[0] == 'file'):
				connection.send("begin")
				print 'receving file...'
				self.receive_file(connection, s[1])
				print 'file received'
			connection.close()

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'Usage: ip port'
	else:
		server = Server(sys.argv[1], int(sys.argv[2]))
		server.run()
