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

		self.logfile = open(self.dir_path + '/' + 'log.txt', 'w')

		if (os.path.exists(Server.config_path) == True):
			f = open(Server.config_path, 'r')
			entry_point = f.readline().split(':')
			f.close()
			self.write_log('Entry_point: %s:%s' %(entry_point[0], entry_point[1]))
			#print 'Entry_point:', entry_point
			self.next_node = self.insert(address = entry_point[0], port = int(entry_point[1]))
		else:
			self.write_log('First node in the circle')
			f = open(Server.config_path, "w")
			f.write(self.address + ':' + str(port))
			f.close()
			self.next_node['address'] = self.address
			self.next_node['port'] = self.port
			self.next_node['hash_code'] = self.hash_code

	def write_log(self, content):
		print content
		self.logfile.write(content + '\n')
		self.logfile.flush()

	def get_next_node(self, address, port):
		#print address, port
		sock = self.connect_node(address, port)
		node_info = self.address + ',' + str(self.port) + ',' + str(self.hash_code)
		buf = struct.pack(header_format, 'find', len(node_info))
		sock.send(buf)
		sock.send(node_info)
		#response
		buf = sock.recv(header_len)
		cmd, datalen = struct.unpack(header_format, buf)
		buf = sock.recv(datalen)
		s = buf.split(',')
		sock.close()
		return {'address': s[0], 'port': int(s[1]), 'hash_code': s[2]}

	def insert(self, address, port):
		next_node = {'address': self.address, 'port': self.port, 'hash_code': self.hash_code}
		if (self.address == address and port == self.port):
			return next_node
		return self.get_next_node(address, port)

	def connect_node(self, address, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((address, port))
		return sock

	def show_next(self, first_node):
		if (first_node == self.next_node['address'] + ":" + str(self.next_node['port'])):
			return ""
		#print first_node
		#print self.next_node['address'], self.next_node['port']
		sock = self.connect_node(self.next_node['address'], self.next_node['port'])
		buf = struct.pack(header_format, 'show', len(first_node))
		sock.send(buf)
		sock.send(first_node)
		buf = sock.recv(header_len)
		cmd, datalen = struct.unpack(header_format, buf)
		buf = sock.recv(datalen)
		sock.close()
		return buf

	def is_middle(self, left_node, right_node, mid_node):
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
		if (self.hash_code == self.next_node['hash_code'] or self.is_middle(self.hash_code, self.next_node['hash_code'], h)):
			res = self.next_node['address'] + ',' + str(self.next_node['port']) + ',' + self.next_node['hash_code']
			self.next_node = new_node
			return res

		#find in next_node
		sock = self.connect_node(self.next_node['address'], self.next_node['port'])
		data = new_node['address'] + ',' + str(new_node['port']) + ',' + new_node['hash_code']
		buf = struct.pack(header_format, 'find', len(data))
		sock.send(buf)
		sock.send(data)
		buf = sock.recv(header_len)
		cmd, datalen = struct.unpack(header_format, buf)
		data = sock.recv(datalen)
		sock.close()
		return data

	def transfer_file(self, address, port, target_hash):
		for file_name in self.files:
			m = hashlib.sha1()
			m.update(file_name)
			file_hash = m.hexdigest()
			if (self.is_middle(file_hash, self.hash_code, target_hash)):
				self.send_file(address, port, file_name)

	def send_file(self, address, port, file_name):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.write_log('Send %s to %s:%s' %(file_name, address, str(port)))
		#print 'Send', file_name, 'to', address, port
		sock.connect((address, port))

		file_path = self.dir_path + '/' + file_name
		buf = struct.pack(header_format, 'file', len(file_name))
		sock.send(buf)
		sock.send(file_name)
		buf_size = 1024
		sock.send(struct.pack("i", os.stat(file_path).st_size))
		fp = open(file_path, "rb")
		while True:
			data = fp.read(buf_size)
			if (not data): 
				break
			sock.send(data)
		sock.close()
		fp.close()
		os.remove(file_path)
		self.files.remove(file_name)

	def receive_file(self, connection, file_name):
		buf = connection.recv(struct.calcsize("i"))
		#unpack return a tuple
		file_size = struct.unpack("i", buf)[0]
		#print 'file size:', file_size
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

	@staticmethod
	def send_data(connection, data):
		buf = struct.pack(header_format, 'RRRR', len(data))
		connection.send(buf)
		connection.send(data)

	def find_file_position(self, file_hash):
		if (self.hash_code == self.next_node['hash_code'] or self.is_middle(self.hash_code, self.next_node['hash_code'], file_hash)):
			return self.next_node['address'] + ',' + str(self.next_node['port'])

		sock = self.connect_node(self.next_node['address'], self.next_node['port'])
		data = file_hash
		buf = struct.pack(header_format, 'posi', len(data))
		sock.send(buf)
		sock.send(data)

		buf = sock.recv(header_len)
		cmd, datalen = struct.unpack(header_format, buf)
		data = sock.recv(datalen)
		sock.close()
		return data


	def find_upload_entry(self, file_name):
		m = hashlib.sha1()
		m.update(file_name)
		file_hash = m.hexdigest()
		return self.find_file_position(file_hash)

	def run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((self.address, self.port))
		print 'Serving at ' + self.address + ':' + str(self.port)
		sock.listen(5)
		# a new inserted node need to get files from its succesor
		if (self.next_node['hash_code'] != self.hash_code):
			ss = self.connect_node(self.next_node['address'], self.next_node['port'])
			data = self.address + ',' + str(self.port) + ',' + self.hash_code
			buf = struct.pack(header_format, 'tran', len(data))
			ss.send(buf)
			ss.send(data)
			ss.close
		while True:
			print '----------------------------\nWaiting for new request...'
			connection, address = sock.accept()
			buf = connection.recv(header_len)
			cmd, datalen = struct.unpack(header_format, buf)
			s = []
			self.write_log('Command: %s' % cmd)
			#print cmd
			if (datalen > 0):
				buf = connection.recv(datalen)
				s = buf.split(',')
			#print s, datalen, buf
			if (cmd == 'tran'):
				self.transfer_file(s[0], int(s[1]), s[2])
			elif (cmd == 'find'):
				#print s[0], s[1], s[2]
				data = self.find({'address': s[0], 'port': int(s[1]), 'hash_code': s[2]})
				Server.send_data(connection, data)
			elif (cmd == 'posi'):
				#print s[0]
				data = self.find_file_position(s[0])
				Server.send_data(connection, data)
			elif (cmd == 'show'):
				#print cmd
				res = '\n***** ' + self.address + ':' + str(self.port) + ' *****\n'
				if (len(self.files) > 0):
					for fname in self.files:
						res = res + ' ' + fname
				else:
					res = res + ' Nothing!'
				res = res + '\n'
				#print res
				if (len(s) > 0):
					res = res + self.show_next(s[0])
				else:
					res = res + self.show_next(self.address + ":" + str(self.port))
				Server.send_data(connection, res)
			elif (cmd == 'file'):
				self.write_log('Receiving %s' % s[0])
				#print 'Receiving', s[0]
				self.receive_file(connection, s[0])
				self.write_log('%s received!' % s[0])
				#print s[0], 'received!'
			elif (cmd == 'uplo'):
				data = self.find_upload_entry(s[0])
				Server.send_data(connection, data)
			connection.close()

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'Usage: server.py ip port'
	else:
		server = Server(sys.argv[1], int(sys.argv[2]))
		server.run()
