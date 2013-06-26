import socket
import time
import struct
import os

entry_point = {}

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

def trans_address_str(address):
	address = address.split()
	return address[0], int(address[1])

def _upload(address, port, file_path):
	pass

def upload(address, file_path):
	address, port = trans_address_str(address)
	_upload(address, port, file_path)

def _upload_folder(address, port, dir_path):
	file_list = os.listdir(dir_path)
	for file_path in file_list:
		if (os.path.isfile(file_path)):
			_upload(address, port, file_path)
	print dir_path, 'uploaded!'
	
def upload_folder(address, dir_path):
	address, port = trans_address_str(address)
	_upload_folder(address, port, dir_path)

def read_config(config_path):
	f = open(config_path, "r")
	address = f.readline()
	entry_point['address'], entry_point['port'] = trans_address_str(address)
	f.close()

if __name__ == '__main__':
	read_config(config_path)
	print 'Usage:\nupfile ip:port filepath\nupfolder ip:port folder\nlog\n'
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

