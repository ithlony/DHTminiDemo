import os

os.system('clear.bat')
os.system('start python server.py localhost 10000')
fmt = 'start python server.py %s %s'
while True:
	buf = raw_input('Input server ip and port:')
	s = buf.split()
	os.system(fmt %(s[0], s[1]))
