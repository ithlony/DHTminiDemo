import socket
import time
import struct
import os
from package_header import *

entry_point = {}

def trans_address_str(address):
	address = address.split(':')
	return address[0], int(address[1])

def show_log():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((entry_point['address'], entry_point['port']))
	buf = struct.pack(header_format, 'show', 0)
	print buf
	sock.send(buf)
	buf = sock.recv(header_len)
	cmd, datalen = struct.unpack(header_format, buf)
	print cmd, datalen
	buf = sock.recv(datalen)
	print buf
	sock.close()

def send_file(address, port, file_name, file_path):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((address, port))
	buf = struct.pack(header_format, 'file', len(file_name))
	sock.send(buf)
	sock.send(file_name)
	sock.send(struct.pack("i", os.stat(file_path).st_size))
	buf_size = 1024
	fp = open(file_path, "rb")
	while True:
		data = fp.read(buf_size)
		if (not data): 
			break
		sock.send(data)
	fp.close()
	sock.close()

def _upload(address, port, file_name, file_path):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((address, port))

	buf = struct.pack(header_format, 'uplo', len(file_name))
	sock.send(buf)
	sock.send(file_name)

	buf = sock.recv(header_len)
	cmd, datalen = struct.unpack(header_format, buf)
	buf = sock.recv(datalen)
	s = buf.split(',')
	sock.close()
	print s

	send_file(s[0], int(s[1]), file_name, file_path)

def upload(address, file_path):
	address, port = trans_address_str(address)
	_upload(address, port, file_path, file_path)

def _upload_folder(address, port, dir_path):
	file_list = os.listdir(dir_path)
	print dir_path, file_list
	for file_name in file_list:
		file_path = dir_path + '/' + file_name
		if (os.path.isfile(file_path)):
			print file_name
			_upload(address, port, file_name, file_path)
	print dir_path, 'uploaded!'
	
def upload_folder(address, dir_path):
	address, port = trans_address_str(address)
	_upload_folder(address, port, dir_path)

def read_config(config_path):
	f = open(config_path, "r")
	address = f.readline()
	print address
	entry_point['address'], entry_point['port'] = trans_address_str(address)
	f.close()

if __name__ == '__main__':
	read_config('config.txt')
	print 'Usage:\nCommand 1: upfile ip:port filepath\nCommand 2: upfolder ip:port folder\nCommand 3: log\n'
	while True:
		cmd = raw_input('Input your command(Q to exit):')
		cmd = cmd.split()
		if (cmd[0] == 'upfile'):
			upload_file(cmd[1], cmd[2])
		elif (cmd[0] == 'upfolder'):
			upload_folder(cmd[1], cmd[2])
		elif (cmd[0] == 'log'):
			show_log()
		elif (cmd[0] == 'Q'):
			break

