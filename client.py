import socket
import time
import struct
import os
from package_header import *

entry_point = {}
logfile = ''

def trans_address_str(address):
	address = address.split(':')
	return address[0], int(address[1])

def write_log(content):
	print content
	logfile.write(content + '\n')
	logfile.flush()

def show_log():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((entry_point['address'], entry_point['port']))
	buf = struct.pack(header_format, 'show', 0)
	sock.send(buf)
	buf = sock.recv(header_len)
	cmd, datalen = struct.unpack(header_format, buf)
	buf = sock.recv(datalen)
	write_log('The files distribution in each server:\n %s' % buf)
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

	write_log('Uploading %s' % file_name)
	buf = struct.pack(header_format, 'uplo', len(file_name))
	sock.send(buf)
	sock.send(file_name)

	buf = sock.recv(header_len)
	cmd, datalen = struct.unpack(header_format, buf)
	buf = sock.recv(datalen)
	s = buf.split(',')
	sock.close()
	write_log('%s Uploaded!' % file_name)

	send_file(s[0], int(s[1]), file_name, file_path)

def upload_file(address, file_path):
	address, port = trans_address_str(address)
	_upload(address, port, file_path, file_path)

def _upload_folder(address, port, dir_path):
	file_list = os.listdir(dir_path)
	write_log('Upload folder: %s' %dir_path)
	for file_name in file_list:
		file_path = dir_path + '/' + file_name
		if (os.path.isfile(file_path)):
			_upload(address, port, file_name, file_path)
	write_log('%s uploaded!' %dir_path)
	
def upload_folder(address, dir_path):
	address, port = trans_address_str(address)
	_upload_folder(address, port, dir_path)

def read_config(config_path):
	f = open(config_path, "r")
	address = f.readline()
	print 'Entry point:', address
	entry_point['address'], entry_point['port'] = trans_address_str(address)
	f.close()

if __name__ == '__main__':
	print 'Usage:\nCommand 1: upfile ip:port filepath\nCommand 2: upfolder ip:port folder\nCommand 3: log\n'
	read_config('config.txt')
	logfile = open('client_log.txt', 'w')
	while True:
		cmd = raw_input('Input your command(Q to exit, U to show usage):')
		write_log('Command: %s' % cmd)
		cmd = cmd.split()
		if (cmd[0] == 'upfile'):
			upload_file(cmd[1], cmd[2])
		elif (cmd[0] == 'upfolder'):
			upload_folder(cmd[1], cmd[2])
		elif (cmd[0] == 'log'):
			show_log()
		elif (cmd[0] == 'Q'):
			break
		elif (cmd[0] == 'U'):
			print 'Usage:\nCommand 1: upfile ip:port filepath\nCommand 2: upfolder ip:port folder\nCommand 3: log\n'
	log.close()


