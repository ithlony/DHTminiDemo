import socket
import time
import struct
import os
import sys
from package_header import *

def send_req(address, port, code = 'show'):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((address, port))
	print address, port
	if code == 'show':
		show_log(sock)
	else:
		send_file(sock)
	sock.close()

def show_log(sock):
	file_path = "b.txt"
	buf = struct.pack(header_format, 'show', 0)
	print buf
	sock.send(buf)
	buf = sock.recv(header_len)
	cmd, datalen = struct.unpack(header_format, buf)
	print cmd, datalen
	buf = sock.recv(datalen)
	print buf

def send_file(sock):
	file_path = "b.txt"
	buf = struct.pack(header_format, 'file', 5)
	sock.send(buf)
	sock.send(file_path)
	sock.send(struct.pack("i", os.stat(file_path).st_size))
	buf_size = 1024
	fp = open(file_path, "rb")
	while True:
		data = fp.read(buf_size)
		if (not data): 
			break
		sock.send(data)
	fp.close()

if __name__ == '__main__':
	address = 'localhost'
	port = 10000
	argc = len(sys.argv)
	if (argc > 2):
		address = sys.argv[1]
		port = int(sys.argv[2])
	code = "show"
	if (argc == 2):
		code = sys.argv[1]
	elif (argc == 4):
		code = sys.argv[3]
	send_req(address, port, code)
