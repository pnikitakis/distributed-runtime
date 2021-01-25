import socket
import pickle

hosts = {}

tmp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tmp.connect(("8.8.8.8", 80))
ipAddr = tmp.getsockname()[0]
tmp.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		#dhmiourgia sundeshs TCP
s.bind((ipAddr, 0))
port = s.getsockname()[1]

print('Directory for keeping info about remote users!')
print("Directory -- IP: " + str(ipAddr) + " port: " + str(port))
print('\n')

s.listen(100)

while True:
	connection, host_addr = s.accept()		#apodoxh sundesewn
	
	try:
		data = connection.recv(256) 	#apokwdikopihsh kai apothikeush se katallhlo pinaka
		data = data.decode("utf-8")
		
		info, rest_packet = data.split(',', 1)
		
		if info == 'List':
			packet = pickle.dumps(hosts)
			connection.send(packet)	#send listto sender
			
		elif info == 'Join':
			runtime, rest_packet = rest_packet.split(',',1)
			ip_addr, port = rest_packet.split(',',1)
			
			runtime = str(runtime)
			ip_addr = str(ip_addr)
			port = int(port)
			

			hosts[runtime] = [ip_addr, port]
			
			message = ('OK').encode("utf-8")
			connection.send(message)	#send OK to sender
		
		
	finally:
		connection.close()
		
		
	print('------------- Hosts in directory -------------')
	print(hosts)
	print('\n')
	
		
