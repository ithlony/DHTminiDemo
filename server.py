import sys
import socket
import os
import struct
import hashlib
from package_header import *


class Server:
	buf_size = 1024
	config_path = "config.txt"

	def __init__(self, address, port):
		self.address = address
		self.port = port
		self.dir_path = address + '-' + str(port)
		if (os.path.isdir(self.dir_path) == False):
			os.mkdir(self.dir_path)
		self.files = []

		m = hashlib.sha1()
		m.update(address)
		m.update(str(port))
		self.hash_code = m.hexdigest()
		self.next_node = {}

		if (os.path.exists(Server.config_path) == True):
			f = open(Server.config_path, 'r')
			entry_point = f.readline().split(':')
			f.close()
			self.next_node = self.insert(address = entry_point[0], port = int(entry_point[1]))
		else:
			print 'aa'
			f = open(Server.config_path, "w")
			f.write(self.address + ':' + str(port))
			f.close()
			self.next_node['address'] = self.address
			self.next_node['port'] = self.port
			self.next_node['hash_code'] = self.hash_code

	def insert(self, address, port):
		next_node = {'address': self.address, 'port': self.port, 'hash_code': self.hash_code}
		if (self.address == address and port == self.port):
			return next_node
		sock = self.connect_node(address, port)
		sock.send('find,' + self.address + ',' + str(self.port) + ',' + str(self.hash_code))
		sock.close()
		return next_node

	def connect_node(self, address, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((address, port))
		return sock

	def show_next(self, first_node):
		if (first_node == self.next_node['address'] + ":" + str(self.next_node['port'])):
			return ""
		sock = connect(address, port)
		buf = struct.pack(header_format, 'show', len(first_node))
		sock.send(buf)
		sock.send(first_node)
		buf = sock.recv(header_len)
		cmd, datalen = struct.unpack(header_format, buf)
		buf = sock.recv(datalen)
		sock.close()
		return buf

	def is_middle(left_node, right_node, mid_node):
		if (left_node < right_node):
			if (mid_node > left_node and mid_node < right_node):
				return True
		elif (mid_node > left_node or mid_node < right_node):
			return True
		return False

	def find(self, new_node):
		h = new_node['hash_code']
		address = new_node['address']
		port = new_node['port']
		if (self.hash_code == self.next_node['hash_code']):
			#tell the new node about its address, port and hash_code
			sock = self.connect_node(address, port)
			sock.send('next_node,', self.next_node['address'], + ',' + self.next_node['port'] + ',' + self.next_node['hash_code'])
			sock.close()
			#tell the next node to tranfer file to new node
			sock = self.connect_node(next_node['address'], next_node['port'])
			sock.send('transfer,', address + ',' + port + ',' + h) 
			sock.close()
			self.next_node = new_node
			return
		elif (self.is_middle(self.hash_code, self.next_node['hash_code'], h)):
			#tell the new node about its address, port and hash_code
			sock = self.connect_node(address, port)
			sock.send('next_node,', self.next_node['address'], + ',' + self.next_node['port'] + ',' + self.next_node['hash_code'])
			sock.close()
			#tell the next node to tranfer file to new node
			sock = self.connect_node(next_node['address'], next_node['port'])
			sock.send('transfer,', address + ',' + port + ',' + h) 
			sock.close()
			self.next_node = new_node
			return

		sock = self.connect_node(address, port)
		sock.send('find,', address + ',' + port)
		sock.recv(Server.buf_size)
		sock.close()

	def transfer_file(sefl, address, port, target_hash):
		for file_name in files:
			m = hashlib.sha1()
			m.update(file_name)
			file_hash = m.hexdigest()
			if (self.is_middle(file_hash, self.hash_code, target_hash)):
				self.send_file(address, port, file_name)

	def send_file(address, port, file_name):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((address, port))

		file_path = dir_path + '/' + file_name
		sock.send('file,' + file_name)
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
			os.remove(file_path)
			files.remove(file_name)
		sock.close()

	def receive_file(self, connection, file_name):
		buf = connection.recv(struct.calcsize("i"))
		#unpack return a tuple
		file_size = struct.unpack("i", buf)[0]
		print 'file size:', file_size
		file_path = self.dir_path + '/' + file_name 
		fp = open(file_path, "wb")
		while file_size > 0:
			if (file_size < Server.buf_size):
				buf = connection.recv(file_size)
			else:
				buf = connection.recv(Server.buf_size)
			fp.write(buf)
			file_size = file_size - Server.buf_size
		fp.close()
		self.files.append(file_name)

	def run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((self.address, self.port))
		print self.address, self.port
		sock.listen(5)
		header_format = '4si'
		header_len = struct.calcsize(header_format)
		while True:
			connection, address = sock.accept()
			buf = connection.recv(header_len)
			cmd, datalen = struct.unpack(header_format, buf)
			s = []
			#print cmd, datalen
			print cmd
			if (datalen > 0):
				buf = connection.recv(datalen)
				s = buf.split(',')
			#print s, datalen, buf
			if (cmd == 'tran'):
				self.transfer_file(s[0], s[1], s[2])
			elif (cmd == 'find'):
				print s[0], s[1], s[2]
				self.find({'address': s[0], 'port': s[1], 'hash_code': s[2]})
			elif (cmd == 'show'):
				#print cmd
				res = self.address + ':' + str(self.port) + '\n'
				if (len(fname) > 0):
					for fname in self.files:
						res = res + ' ' + fname
				else:
					res = res + 'Nothing!'
				#print res
				if (len(s) > 0):
					res = res + self.show_next(s[0])
				else:
					res = res + self.show_next(self.address + ":" + str(self.port))
				buf = struct.pack(header_format, '1111', len(res))
				print buf
				print res
				connection.send(buf)
				connection.send(res)
			elif (cmd == 'file'):
				print 'receving file...'
				self.receive_file(connection, s[0])
				print 'file received'
			elif (cmd == 'next'):
				self.next_node['address'] = s[0]
				self.next_node['port'] = int(s[1])
				self.next_node['hash_code'] = s[2]
			elif (cmd == 'upload'):
				pass
			connection.close()

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'Usage: server.py ip port'
	else:
		server = Server(sys.argv[1], int(sys.argv[2]))
		server.run()
