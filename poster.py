import socket
import time
import struct
import os

def send_req(address, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((address, port))
	print address, port

	file_path = "a.txt"
	sock.send('file,' + file_path)
	buf = ""
	while (buf != 'begin'):
		buf = sock.recv(5)
	print buf
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

if __name__ == '__main__':
	send_req('localhost', 8000)
