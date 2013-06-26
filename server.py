import sys
import socket
import os
import struct
import hashlib


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

		if (os.path.exist(config_path) == True):
			f = open(config_path, 'r')
			entry_point = f.readline().split(':')
			f.close()
			self.next_node = self.insert(address = entry_point[0], port = int(entry_point[1]))
		else:
			f = open(config_path, "w")
			f.write(self.address + ':' + str(port))
			f.close()
			self.next_node['address'] = self.address
			self.next_node['port'] = self.port
			self.next_node['hash_code'] = self.hash_code

	def insert(address, port):
		sock = self.connect_node(address, port)
		sock.send('find,' + self.address + ',' + str(self.port) + ',' + str(self.hash_code))
		sock.close()

	def connect_node(self, address, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((address, port))
		return sock

	def show_next(self, first_node):
		if (first_node == self.next_node['address'] + ":" + str(self.next_node['port'])):
			return ""
		sock = connect(address, port)
		sock.send('show,' + first_node)
		ret = sock.recv(Server.buf_size)
		sock.close()
		return ret

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
		files.append(file_name)

	def run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((self.address, self.port))
		print self.address, self.port
		sock.listen(5)
		while True:
			connection, address = sock.accept()
			buf = connection.recv(Server.buf_size)
			s = buf.split(',')
			print 'command', s[0]
			if (s[0] == 'transfer'):
				self.transfer_file(s[1], s[2], s[3])
			elif (s[0] == 'find'):
				print s[1], s[2], s[3]
				self.find({'address': s[1], 'port': s[2], 'hash_code': s[3])
			elif (s[0] == 'show'):
				res = self.address + ':' + self.port + '\n'
				for fname in files:
					res = res + fname
				if (len(s) > 1):
					res = res + self.show_next(self.address, s[1])
				else:
					res = res + self.show_next(self.address, self.address + ":" + str(self.port))
				connection.send(res)
			elif (s[0] == 'file'):
				connection.send("begin")
				print 'receving file...'
				self.receive_file(connection, s[1])
				print 'file received'
			elif (s[0] == 'next_node'):
				self.next_node['address'] = s[1]
				self.next_node['port'] = int(s[2])
				self.next_node['hash_code'] = s[3]
			elif (s[0] == 'upload'):
				pass
			connection.close()

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'Usage: ip port'
	else:
		server = Server(sys.argv[1], int(sys.argv[2]))
		server.run()
