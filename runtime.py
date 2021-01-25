import os
import threading
import time
import ast
import configuration
from socket import *
import socket
import pickle


threadsArray = []  		#pinakasapo threads
tuples_dict = {}

programs_dict = {}
temp_label_dict = {}
filename_dict = {}


progr_id = 0			#id gia kathe programma
flagStop = []			#flag gia na termatistei to programma enw trexei akoma
flagEnd = []			#flag oti h ektelesh programamtos exei termatisei akoma kai an den eei ginei exit

#locksss
tuple_lock = threading.Lock()
flagStop_lock = threading.Lock()
event_tuple = threading.Event()		#dhmiourgia event gia kathe ena thread

broadcast_IP = '255.255.255.255'
udp_port = 12345

dirIP = ''		#arxikopoihshs timwn tou directory
dirPort = 0


class codeThread(threading.Thread):		#directory thread
	def __init__(self, progr_id):
		threading.Thread.__init__(self)
		self.progr_id = progr_id
	def run(self):
		code_implemetation(self.progr_id)


class recv_tcp_thread(threading.Thread):		#thread gia recv aithmatwn mesw tcp
	def __init__(self, sender_ip, sender_port):
		threading.Thread.__init__(self)
		self.sender_ip = sender_ip
		self.sender_port = sender_port
	def run(self):
		tuple_over_TCP(self.sender_ip, self.sender_port)
	
class recv_udp_thread(threading.Thread):		#thread gia recv aithmatwn mesw tcp
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		receiver_UDP()

class tcp_recv_code_thread(threading.Thread):		#thread gia recv kwdika mesw tcp apo apomakrusmena periballonta
	def __init__(self, ipaddr, port):
		threading.Thread.__init__(self)
		self.ipaddr = ipaddr
		self.port = port
	def run(self):
		tcp_rcv_code(self.ipaddr, self.port)
	

class tcp_send_code_thread(threading.Thread):		#thread gia recv kwdika mesw tcp apo apomakrusmena periballonta
	def __init__(self, progr_id, ip_addr, port):
		threading.Thread.__init__(self)
		self.progr_id = progr_id
		self.ip_addr = ip_addr
		self.port = port
	def run(self):
		tcp_send_code(self.progr_id, self.ip_addr, self.port)
	
	
def setdir(ipaddr, port):
	global dirIP
	global dirPort

	dirIP = str(ipaddr)
	dirPort = int(port)
	
	return	

	
## CHECKING OF SYNTAX 
def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


def check_var(var):
	if var[0] != '$':
		return -1
	
	return 0
	
	
def check_varValS(varVal):
	if varVal[0] != '$': #if not variable
		if varVal[0] != '"' or varVal[-1] != '"': #if not integer
			return -1
	
	return 0


def check_varValI(varVal):
	if varVal[0] != '$': #if not variable
		if check_int(str(varVal)) == False: #if not integer
				return -1
	
	return 0


def check_varVal(varVal):
	if check_varValI(varVal) == -1:
		if check_varValS(varVal) == -1:
			return -1
		
	return 0

def checkSyntax(line, pc):
	global temp_label_dict
	
	instrSet1 = ['ADD', 'SUB', 'MUL', 'DIV', 'MOD']
	instrSet2 = ['BGT', 'BGE', 'BLT', 'BLE', 'BEQ']

	line = line.strip()
	#print('line in checkSyntax: ', line)
	try:
		if line[0] == '#':
			label, line = line.split(' ',1) #afairesh label
			temp_label_dict[label] = pc #gia na eleksoume ean ksepernaei ton arithmo entolwn
			line = line.strip()
			label = label.strip()
			
		instr, line = line.split(' ', 1)
		line = line.strip()
		instr = instr.strip()
		
		if instr in instrSet1:
			var, varVal1, varVal2 = line.split()
			r1 = check_var(var)
			r2 = check_varValI(varVal1)
			r3 = check_varValI(varVal2)	
			if(r1 == -1) or (r2 == -1) or (r3 == -1):
				return -1
		elif instr in instrSet2:
			varVal1, varVal2, label = line.split()
			r1 = check_varValI(varVal1)
			r2 = check_varValI(varVal2)
			if(r1 == -1) or (r2 == -1):
				return -1
		elif instr == 'BRA':
			label = line
			if label[0] != '#':
				return -1
		elif instr == 'SET':
			var, varVal = line.split()
			r1 = check_var(var)
			r2 = check_varVal(varVal)
			
			if(r1 == -1) or (r2 == -1):
				return -1
		elif instr == 'SLP':
			varVal = line
			r1 = check_varValI(varVal)
			if r1 == -1:
				return -1
		elif instr == 'PRN':#line PRN "first argument is:" $argv[0] $b " world " $a
			curr_pos = 0

			while curr_pos < len(line):
				if line[curr_pos] == '"':		#an uparxei string
					fir_pos = curr_pos			#prwth emfanish
					sec_pos = line[fir_pos+1:].index('"')	#deyterh emfanish

					curr_pos += (sec_pos + 2)
				elif line[curr_pos] == '$':		#an prokeitai gia metablhth
					try:
						fir_pos = line[curr_pos+1:].index(' ')		#bres mexri to prwto keno meta to $

						var =  line[curr_pos:fir_pos+curr_pos+1]
						
						r1 = check_var(str(var))
						if (r1 == -1):
							return -1

						curr_pos += (fir_pos1)
					except:					#an den exei keno shmainei oti eimai sto telos
						var =  line[curr_pos:]		#pare th metablhth mexri to telos
						
						r1 = check_var(str(var))
						if (r1 == -1):
							return -1

						curr_pos = len(line)
				else:
					curr_pos += 1
		
		elif instr == 'PUT':
			varValS, varVal = line.split(' ', 1)
			
			r1 = check_varValS(varValS)
			#r2 = check_varVal(varVal)
			if r1 == -1:
				return -1
		elif instr == 'GET':
			varValS, varVal = line.split(' ', 1)
			r1 = check_varValS(varValS)
			#r2 = check_varVal(varVal)
			if r1 == -1:
				return -1
		
		elif instr == 'DEL':
			var = line
			
			r1 = check_var(var)
			if(r1 == -1):
				return -1
		else:
			return -1
			
	except: #exoume 1 mono leksi ana grammi
		if line != 'EXT':
			return -1
	
	return 0
## ENd OF CHECKING SYNTAX


## EACH THREAD RUNS THIS CODE
def code_implemetation(progr_id):
	global programs_dict
	global flagStop 
	
	progr_id = int(progr_id)
	
	instrSet1 = ['ADD', 'SUB', 'MUL', 'DIV', 'MOD']
	instrSet2 = ['BGT', 'BGE', 'BLT', 'BLE', 'BEQ']
	
	if progr_id in programs_dict.keys():			#eyresh kwdika tou antisoixou programmatos (progr_id)
		code = programs_dict[progr_id][1][:]
		variables = programs_dict[progr_id][2]
	
	#line = 0
	line = programs_dict[progr_id][0]		#pairnw kathe fora to program_counter PC
	while line < len(code):
		#check if kill or transfer
		if flagStop[progr_id] == True:
			programs_dict[progr_id][0] = line
			programs_dict[progr_id][2] = variables
			flagStop[progr_id] = False #enhmerwse to kurio thread pws exoume teleiwsei
			return
		
		if code[line][0] == 'PRN':		#['PRN', '"first argument is:"', '$argv[0]'] morfh
			pos_remaining = 1		#to 0 einai to print
			
			while pos_remaining < len(code[line]):
				if '"' in code[line][pos_remaining]:
					prn_str = code[line][pos_remaining].replace('"','')
					print(prn_str, end=' ')
					pos_remaining+=1
			
				elif '$' in code[line][pos_remaining]:
					try:
						prn_var = variables[code[line][pos_remaining]]
						print(prn_var, end=' ')
						pos_remaining+=1
					except:
						print('\nERROR: Variable not found! line: ', line)
						return
			print()
			
		elif code[line][0] == 'SET':
			var = code[line][1]
			varVal = code[line][2]
			
			r = check_var(varVal)

			if r == 0:
				try:
					varVal_val = variables[varVal]
				except:
					print('\nERROR: Variable not found! line: ', line)
					return
			else:
				if check_int(str(varVal)) == True:
					varVal_val = int(varVal)
				else:
					varVal_val = varVal
				
			variables[var] = varVal_val
		
		elif  code[line][0] in instrSet1:
			var = code[line][1]
			varVal1 = code[line][2]
			varVal2 = code[line][3]
		
			r1 = check_var(varVal1)
			
			if r1 == 0:			#an exei mprosta $
				try:
					varVal1_val = variables[varVal1]
				except:
					print('ERROR: Variable not found! line: ', line)
					return	
			else:
				varVal1_val = int(code[line][2])
			
			r2 = check_var(varVal2)
			
			if r2 == 0:			#an exei mprosta $
				try:
					varVal2_val = variables[varVal2]
				except:
					print('ERROR: Variable not found! line: ', line)
					return
			else:
				varVal2_val = int(code[line][3])
			
			if code[line][0] == 'ADD':
				variables[var] = int(int(varVal1_val) + int(varVal2_val))
			
			elif code[line][0] == 'SUB':
				variables[var] = int(int(varVal1_val) - int(varVal2_val))
			
			elif code[line][0] == 'DIV':
				variables[var] = int(int(varVal1_val) / int(varVal2_val))
			
			elif code[line][0] == 'MUL':
				variables[var] = int(int(varVal1_val) *int( varVal2_val))
				
			elif code[line][0] == 'MOD':
				variables[var] = int(int(varVal1_val) % int(varVal2_val))

		elif code[line][0] in instrSet2:
			varVal1 = code[line][1]
			varVal2 = code[line][2]
			label = code[line][3]
			
			r1 = check_var(varVal1)
			
			if r1 == 0:			#an exei mprosta $
				try:
					varVal1_val = variables[varVal1]
				except:
					print('ERROR: Variable not found! line: ', line)
					return
			else:
				varVal1_val = int(code[line][1])
			
			r2 = check_var(varVal2)
			
			if r2 == 0:			#an exei mprosta $
				try:
					varVal2_val = variables[varVal2]
				except:
					print('ERROR: Variable not found! line: ', line)
					return
			else:
				varVal2_val = int(code[line][2])
			
			if code[line][0] == 'BGT':
				if int(varVal1_val) > int(varVal2_val):
					line = int(label)
					continue
				
			elif code[line][0] == 'BGE':
				if int(varVal1_val) >= int(varVal2_val):
					line = int(label)
					continue
				
			elif code[line][0] == 'BLT':
				if int(varVal1_val) < int(varVal2_val):
					line = int(label)
					continue
			
			elif code[line][0] == 'BLE':
				if int(varVal1_val) <= int(varVal2_val):
					line = int(label)
					continue
			
			elif code[line][0] == 'BEQ':
				if int(varVal1_val) == int(varVal2_val):
					line = int(label)
					continue
		elif code[line][0] == 'BRA':
			label = code[line][1]
			line = int(label)
			continue
			
		elif code[line][0] == 'SLP':
			varVal1 = code[line][1]
			
			r1 = check_var(varVal1)
			
			if r1 == 0:			#an exei mprosta $
				try:
					varVal1_val = variables[varVal1]
				except:
					print('ERROR: Variable not found! line: ', line)
					return
			else:
				varVal1_val = int(code[line][1])

			time.sleep(varVal1_val)
			
		elif code[line][0] == 'DEL':
			var = code[line][1]
			
			try:
				del programs_dict[progr_id][2][var]
			except:
				print('ERROR: Variable not found! line: ', line)
				return
		elif code[line][0] == 'PUT':
			tuple_space = code[line][1][:]
			input_tuple = code[line][2][:]
			
			
			r1 =  check_var(tuple_space)
			if r1 == 0:			#an exei mprosta $
				try:
					tuple_space = variables[tuple_space]
				except:
					print('ERROR: Variable not found! line: ', line)
					return
				
			for i in input_tuple:
				if check_int(str(i)) == False:
					if i[0] == '$':
						if i in variables:
							input_tuple[input_tuple.index(i)] = variables[i]
							
			ret = control_tuples('PUT', tuple_space, input_tuple)
			#if ret == 0:
				#print('PUT was succesfull')
		
		elif code[line][0] == 'GET':
			tuple_space = code[line][1][:]
			input_tuple = code[line][2][:]
			
			r1 =  check_var(tuple_space)
			if r1 == 0:			#an exei mprosta $
				try:
					tuple_space = variables[tuple_space]
				except:
					print('ERROR: Variable not found! line: ', line)
					return
				
			for i in input_tuple:
				if check_int(str(i)) == False:
					if i[0] == '$':
						if i in variables:
							input_tuple[input_tuple.index(i)] = variables[i]
				
			ret = control_tuples('GET', tuple_space, input_tuple)
		
			for i in input_tuple:
				if check_int(str(i)) == False:
					if i[0] == '$':
						variables[i] = ret[input_tuple.index(i)]
			
		elif code[line][0] == 'EXT':	
			programs_dict.pop(progr_id, None)	
			break
	
		line += 1
	
	print('----->tuples_dict: ', tuples_dict)

	flagEnd[progr_id] = True		#eidopoihsh oti exei ftasei sto telos
	
	return


def control_tuples(instr, tuple_space, input_tuple):
	global tuples_dict
	
	#lock for tuples
	tuple_lock.acquire()

	if tuple_space not in tuples_dict:
		if configuration.flagDistributed == True:
			ret = find_tuple_broadcast(instr, tuple_space, input_tuple)
			
			if ret == 0:		#den hrthe apanthsh me ok ara den exei kaneis thn pleiada
				tuples_dict[tuple_space] = []
			else:		#uparxei allou h pleiada kai egine h entolh (put h get)
				if instr == 'PUT':
					ret  = 0
				elif instr == 'GET':
					ok_flag, rcv_tuple = ret.split(b',')	#dhmiourgia pleiadas
					
					ret = pickle.loads(rcv_tuple)			#apokwdikopoihsh pleiadas
				
				tuple_lock.release()	
				return ret		#epistrofh eite 0 gia put eite pleiada gia get
		else:
			tuples_dict[tuple_space] = []
				
	if instr == 'PUT':
		tuples_dict[tuple_space].append(input_tuple)
		event_tuple.set()			#eidopoihsh notify gia pleiada!
		event_tuple.clear()

		tuple_lock.release()	
			
		return 0
	
	elif instr == 'GET':
		ret = -1
		total_hits = 0
		for i in input_tuple: #poses times exoume sto tuple
			if check_int(str(i)) == True:
				total_hits += 1
			elif i[0] != '$':
				total_hits += 1
		
		while ret == -1: #gia na einai blocking h get 
			for y in tuples_dict[tuple_space]:
				if len(y) != len(input_tuple):
					continue
				hits = 0
				for x in input_tuple:
					if x == y[input_tuple.index(x)]: 
						hits += 1
						if hits == total_hits:
							ret = y
							delIndex = tuples_dict[tuple_space].index(y)
							break
				
			if ret == -1: #den brhkame tuple
				print('Waiting for tuple: ', input_tuple)
				tuple_lock.release()
				event_tuple.wait() 		#to sugkekrimeno thread mplokare

				tuple_lock.acquire()			#acquire otan xupnhsei gia to while loop
		
		tuples_dict[tuple_space].pop(delIndex)
		if not tuples_dict[tuple_space]:			#diagrafh pleiadas an einai adeia
			del tuples_dict[tuple_space]
		
		tuple_lock.release()
		return ret
		
	
#h pleiada tuple den uparxei topika sto diko mas dictionary ara prepei na steiloyme se olous
#osous nhkoun sto idio diktyo gia na anakalupsoume thn pleiada
def find_tuple_broadcast(instr, tuple_space, input_tuple):
	tmp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	tmp.connect(("8.8.8.8", 80))
	ip_addr = tmp.getsockname()[0]			#get my ip
	port = tmp.getsockname()[1]				#get my port
	tmp.close()
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	
	#create packet
	ip_addr = str(ip_addr)
	port = str(port)
	tuple_space = str(tuple_space)
	
	packet = (ip_addr + ',' + port + ',' + tuple_space).encode("utf-8")
		
	s.sendto(packet,(broadcast_IP,udp_port))
	
	s.close()			#elegxos alla apo terminal etrexe komple
	
	ret = send_tuple_tcp(ip_addr, port, instr, tuple_space, input_tuple)			#dhmiourgia sundeshs tcp gia aostolh pleiadas
	
	if ret == 0:			#h pleidada den uparxei allou
		return 0
	else:
		return ret			#h pleiada uparxei aki epistrfetai to apotelesma
	


#dhmourgia sundeshs tcp gia na steilw tuple_space kai input_tuple 
def send_tuple_tcp(ip_addr, port, instr, tuple_space, input_tuple):
	TCP_IP = str(ip_addr)
	TCP_PORT = int(port)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((TCP_IP, TCP_PORT))

	s.listen(1)			#timeout
	s.settimeout(5)
	
	try:
		conn, addr = s.accept()		#address einai h dieuthunsh apo ton oopoioo paralambanoume mhnumata
	except socket.timeout:
		print('timeout tcp communication in send_tuple_tcp\n')
		return 0
	
	input_tuple = pickle.dumps(input_tuple)		#metatroph pinaka se packet gia tcp
	packet = (instr + ',' + tuple_space +',').encode("utf-8")
	packet += input_tuple
	
	conn.send(packet)
	
	while True:
		data = conn.recv(2048)	#buffer size
		
		if data != None:
			if b'OK' in data:
				return data
			elif b'OK' not in data:
				return 0
		else:
			return 0
	

#sunarthsh gia apostolh pleiadas ara shmainei oti exw sigoura thn pleiada 
def tuple_over_TCP(sender_ip, sender_port):
	address = (sender_ip, sender_port)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.settimeout(None) #blocking - den kleinei h tcp mexri na epistrepsoume apotelesma
	sock.connect(address)
	
	data = sock.recv(2048)
	instr, tuple_space, tuple_input = data.split(b',')
	
	instr = instr.decode("utf-8")
	tuple_space = tuple_space.decode("utf-8")
	tuple_input = pickle.loads(tuple_input)

	ret = control_tuples(instr, tuple_space, tuple_input)
	
	if instr == "PUT":
		packet = ('OK').encode("utf-8")
	elif instr == 'GET':
		packet = ('OK,').encode("utf-8")
		ret = pickle.dumps(ret)		#metatroph pinaka se packet gia tcp
		packet += ret

	sock.send(packet)
	
	sock.close()
	
	return 


#na baloyme to port = 12345 san global metbliti gia na to exei to ka8e runtime
def receiver_UDP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)			#gia na mporw na exw parapanw apo mia sundeseis
	s.bind(('', udp_port))
	
	while True:
		msg, sender_addr = s.recvfrom(1024)			#to mhnuma periexei to ip kai port tou 
		
		msg = msg.decode("utf-8")
		sender_ip, sender_port, tuple_space = msg.split(',')

		sender_ip = (sender_ip).strip()
		sender_port = int(sender_port) 	
		tuple_space = tuple_space.strip()
	
		if tuple_space in tuples_dict:			#exw thn pleiada
			th = recv_tcp_thread(sender_ip, sender_port)
			th.start()

	return
	
	
def join_directory(runtime):
	global dirIP
	global dirPort

	tmp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	tmp.connect(("8.8.8.8", 80))
	ip_addr = tmp.getsockname()[0]			#get my ip
	port = tmp.getsockname()[1]				#get my port
	tmp.close()
	

	#apostolh mhnumatos sto directory
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	#dhmiourgia sundeshs TCP
		s.connect((dirIP, dirPort))			#tha ta parw apo to input me thn grp_setdir
	except:
		print('Need IP address and Port of directory! Give instruction [directory] first...\n')
		return 0
	
	try:		#apostolh mhnumatos sto directory
		message = 'Join,' + str(runtime) + ',' + str(ip_addr) + ',' + str(port)
		message = message.encode('utf-8')
		s.sendall(message)
		
		# Look for the response
		data = s.recv(256) 		#increase for more team members - data = OK, totalIDs, flagSequencer
		data = data.decode('utf-8')
	finally:
		s.close()
		
	if data != 'OK':		#elegxos an erthei error
		print('Error in connection with directory!')
		return 0
	
	th2 = tcp_recv_code_thread(ip_addr, port)		#thread se while True gia apodoxh kwdika mesw tcp
	th2.start()
	
	return 1
	
	
def tcp_send_code(progr_id, ip_addr, port):
	global programs_dict
	global filename_dict
	
	#create tcp connection
	ip_addr = str(ip_addr)
	port = int(port)
	progr_id = int(progr_id)
	filename = filename_dict[progr_id]
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.settimeout(None) #blocking - den kleinei h tcp mexri na epistrepsoume apotelesma
	
	try:
		sock.connect((ip_addr, port))
	except:
		print('No  such ip address and port for sending code!')
		return
	
	#create packet
	packet = programs_dict[progr_id]
	packet.append(filename)
	packet = pickle.dumps(packet)		#kwdikopoihsh oloklhrou pinaka
	
	#send packet
	sock.send(packet)
	
	sock.close()
	
	programs_dict.pop(progr_id, None)	#afairesh programmatos apo ton pinaka
	del filename_dict[progr_id]			#diagrafh apo to dictionary
	return 
	
	
def tcp_rcv_code(ip_addr, port):
	global filename_dict
	
	ip_addr = str(ip_addr)
	port = int(port)
	
	#dhmiurgia sundeshs tcp gia paodoxh mhnumtwn kwdika
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((ip_addr, port))
	
	s.listen(100)
	while True:
		conn, addr = s.accept()
		
		data = conn.recv(2048)#recv mhnuma me code klp kai apokwdikopoish
		
		#apokwdikopoihsh
		data = pickle.loads(data)	#data ths morfhs: [line, [code], {variables}, filename]

		line = data[0]
		code = data[1]
		variables = data[2]
		filename = data[3]
		
		flagStop_lock.acquire()

		progr_id = len(programs_dict)		#h aritmhsh xekianei apo to 0
		
		filename_dict[progr_id] = filename
		programs_dict[progr_id] = [line, code, variables]
		flagStop.append(False)
		flagEnd.append(False)
		
		th1 = codeThread(progr_id)
		th1.start()

		flagStop_lock.acquire()
			
	return #den tha ftasei pote edw
	
	
# migrate 0 192.168.1.106 53598
		
## PROGRAM STARTS HERE
#runtime's threads

args = input('~~~~~~~~~\Set directory <ip> <port>: ~~~~~~~~~ \n')
args = args.split() #pinakas me ola ta flags
args = [x.strip() for x in args]

dir_ipaddr = str(args[0])
dir_port = int(args[1])

setdir(dir_ipaddr, dir_port)

runtime = input('~~~~~~~~~ Join directory (Give name of runtime)~~~~~~~~~ \n')

ret = join_directory(runtime)
while ret == 0:
	runtime = input('~~~~~~~~~ Join directory (Give name of runtime)~~~~~~~~~ \n')
	ret = join_directory(runtime)

th1 = recv_udp_thread()		#thread se while True gia apodoxh udp broadcast
th1.start()

time.sleep(2)




while True:
	args = input('~~~~~~~~~\nGive instruction [run] [migrate] [list] [kill] [shutdown]: \n')
	args = args.split() #pinakas me ola ta flags
	args = [x.strip() for x in args]


	if args[0] == 'run':
		args.pop(0)
		try:
			f = open(args[0], 'r')
		except:
			print('Error at opening source code file. Continuing at next instruction\n')
			continue
		
		code = []
		pc = 0
		for line in f:
			line = str(line)
			line = line.replace('\t', ' ') 
			line = line.strip()

			if line == '':
				continue
			
			if pc == 0:
				if line == "#SIMPLESCRIPT":
					continue

			ret = checkSyntax(line, pc)
			if ret == -1:
				print('Syntax error at line (lines counting from 1 and not counting empty lines): ', pc + 2)
				print('Continuing at next instruction\n')
				break
			else:
				if 'PUT' in line or 'GET' in line:
					if line[0] == '#':
						l, line = line.split(' ',1)
						line = line.strip()
					instr, line = line.split(' ',1)
					instr = instr.strip()
					line = line.strip()
					t_space, line = line.split(' ',1)
					t_space = t_space.strip()
					line = line.strip()
					line = line[1:-1]

					tmp = line.split(',')
					array = []
					for i in tmp:
						t = i.strip()
						if check_int(str(t)) == True:
							t = int(t)
						try:
							t = ast.literal_eval(i)
						except:
							pass
						array.append(t)
						line = array[:]

					temp_array = [instr, t_space, line]

				elif 'PRN' in line:
					temp_array = []			#morfh grammhs  PRN "first argument is:" $argv[0] " world " $a
					curr_pos = 3 		#3(prn)
					temp_array.append('PRN')
					
					while curr_pos < len(line):
						
						if line[curr_pos] == '"':			#an exw mesa string

							fir_pos = curr_pos				#prwth thesh "
							sec_pos = line[fir_pos+1:].index('"')		#deyterh thesh "
							
							string = line[fir_pos:fir_pos + sec_pos+2]		#apothikeysh antistoixoy string
							temp_array.append(string)
							
							curr_pos += (sec_pos +2)
							
						elif line[curr_pos] == '$':			#an prokeitai gia metablhth
							try:
								fir_pos = line[curr_pos:].index(' ')		#bres mexri to prwto keno an uparxei

								var =  line[curr_pos:curr_pos+fir_pos]		#apothiekush metablhths
								temp_array.append(var)
								curr_pos += (fir_pos)
								
							except:					#an den exei keno shmainei oti eimai sto telos
								temp_array.append(line[curr_pos:])
								curr_pos = len(line)
						else:	#diaforetika apla metkainshe to curr_pos
							curr_pos += 1
				else:
					temp_array = line.split()
					
				for i in temp_array:
					try:
						temp_array[temp_array.index(i)].strip()
					except:
						pass

				code.append(temp_array)
			pc += 1
		
		if ret == -1:
			temp_label_dict.clear() #mhdenismos tou dict afoy den to xreiazomaste allo
			f.close()
			continue
		
		#replace labels
		for i in code:
			if i[0][0] == "#":
				i.pop(0)
			
			if i[-1][0] == '#':
				if i[-1] in temp_label_dict:
					i[-1] = temp_label_dict[i[-1]]
				else:
					print('Syntax error at line (lines counting from 1): ', i + 1)
					print('Continuing at next instruction\n')
					temp_label_dict.clear() #mhdenismos tou dict afoy den to xreiazomaste allo
					f.close()
					continue
				
		variables = {}
		cnt=0
		for i in args:
			v = '$argv'+ '['+ str(cnt)+']'
			variables[v] = i
			cnt+=1
			
		flagStop_lock.acquire()
		flagStop.append(False)
		flagEnd.append(False)

		programs_dict[progr_id] = [0, code, variables]
		filename_dict[progr_id] = args[0]
		
		#create thread for every code
		th1 = codeThread(progr_id)
		th1.start()
		
		threadsArray.append(th1)
		
		progr_id += 1
		flagStop_lock.release()
		
		temp_label_dict.clear() #mhdenismos tou dict afoy den to xreiazomaste allo
		f.close()
		
	elif args[0] == 'migrate':
		progr_id = int(args[1])		#programma gia metanasteysh
		ip_addr = str(args[2])		#ip address kai port tou neou host
		port = int(args[3])
		
		if progr_id not in programs_dict:
			print('No such progr_id (file) for migration!\n')
			continue
		
		#stop my program and get the stop_line
		flagStop[progr_id] = True		#stop the program
		
		while (flagStop[progr_id] == True):		#mplokarisma
			pass
		
		#create a thread for sending code at the nnew host(ip, port)
		th = tcp_send_code_thread(progr_id, ip_addr, port)
		th.start()
		

		
	elif args[0] == 'list':
		args = []
		#!!! lock
		print(programs_dict)
		for key, value in programs_dict.items():
			args = []
			for i in value[2]:
				if i[:6] == '$argv[':
					args.append(value[2][i])#str(value[2]['$argv[0]'])
			print('ID: ' + str(key) + ' Args: ', end='')
			print(args)
		
		print('tuples: ')
		print(tuples_dict)
		print('filename_dict: ')
		print(filename_dict)
		
	elif args[0] == 'kill':
		print('programs_dict: ', programs_dict)
		progr_id = int(args[1])
		
		if flagEnd[progr_id] == True:	#an to programma exei ektelesei ton kwdika tou
			if progr_id not in programs_dict:
				print('No program with that id')
				print('Continuing at next instruction\n')
				continue
			else:		#to programma uparxei kai den exei ginei exit
				r = programs_dict.pop(progr_id, None) 	
				if r != None:
					print("Deletion was succesfull\n")
		else:
			flagStop[progr_id] = True		#douleuei mono otan to programma trexei akoma
			while flagStop[progr_id] != False:
				time.sleep(1) #wait until program stop
				
			r = programs_dict.pop(progr_id, None) 	
			if r != None:
				print("Deletion was succesfull\n")
		
	elif args[0] == 'shutdown':
		pass
	else:
		print('Wrong instruction. Continuing at next instruction\n')


	