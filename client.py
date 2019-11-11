import socket
import socketserver
import sys
import _thread

mensagens = []
listenerPort = 0
serverPort = 8000
serverAddress = ""

ultimaMsg = 0


if(len(sys.argv) < 2):
	print("Erro: %s <ip_servidor>" %sys.argv[0])
	exit()
host = sys.argv[1]

def getMensagens(threadname):
	global serverPort
	global serverAddress
	global ultimaMsg
	while(True):
		try:
			if(mensagens[ultimaMsg] != ""):
				ultimaMsg = ultimaMsg + 1
				continue
		except Exception as e:
			pass

		endereco = ""
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((serverAddress, serverPort))
			sock.sendall(bytes(str("1;" + str(ultimaMsg)), "utf-8")) #Pedimos a proxima mensagem
			endereco = str(sock.recv(1024), "utf-8") #Servidor retorna ip e porta de alguem que tenha esta mensagem
		except:
			continue
		finally:
			sock.close()


		if(endereco == "0"): #Número de mensagem ainda não registrado no servidor
			continue
		else:
			endereco = endereco.split(";")
			mensagem = ""
			try:
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.connect((str(endereco[0]), int(endereco[1])))
				sock.sendall(bytes(str("0;" + str(ultimaMsg)), "utf-8")) #Pedimos a proxima mensagem
				mensagem = str(sock.recv(1024), "utf-8") #Outro cliente retorna a mensagem
			except:
				continue
			finally:
				sock.close()
			#print(mensagem)
			nomeArquivo = nome + "-"+ str(ultimaMsg) + ".client"
			arq = open(nomeArquivo,'w+')
			arq.write(mensagem)
			arq.close()

			if(ultimaMsg < len(mensagens)):
				mensagens[ultimaMsg] = mensagem
			else:
				mensagens.append(mensagem)
			try:
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.connect((serverAddress, serverPort))
				sock.sendall(bytes(str("2;" + str(ultimaMsg) + ";" + str(listenerPort)), "utf-8")) #Informamos ao server que recebemos a mensagem
			except:
				continue
			finally:
				sock.close()
			ultimaMsg = ultimaMsg + 1


def listenClientRequests(threadname):

	global listenerPort

	class ClientRequestHandler(socketserver.BaseRequestHandler):

		def handle(self):
			global mensagens
			self.data = self.request.recv(1024).strip()
			data = self.data.decode("utf-8")
			data = data.split(";")

			if(data[0] == "0"):  #Outro cliente solicita a mensagem i

				# Recebe no formato: '0;i', onde i é a mensagem solicitada
				self.request.sendall(bytes(mensagens[int(data[1])], "utf-8")) #Retornamos a mensagem solicitada



	# Ouvir em todas as interfaces desta máquina
	HOST = '0.0.0.0'

	try:
		server = socketserver.TCPServer((HOST, 0), ClientRequestHandler)
		listenerPort = server.server_address[1] #Obtemos o número da porta randomica designada ao listener
		server.serve_forever()
	except KeyboardInterrupt:
		server.server_close()


try:
	nome = ""
	print("Informe seu nome.")
	nome = input()
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((serverAddress, serverPort))
		sock.sendall(bytes(str("3"), "utf-8")) #Informamos ao servidor que uma nova mensagem foi criada
		ultimaMsg = str(sock.recv(1024), "utf-8") #Ele nos retorna o número de mensagem que registrou
		ultimaMsg = int(ultimaMsg) + 1
	finally:
		sock.close()
	print("Deseja mandar e receber um arquivo?")
	print("0 - Sim")
	print("1 - não")
	resposta = input();

	if(resposta == "0"):



		_thread.start_new_thread(getMensagens, ("getter",))
		_thread.start_new_thread(listenClientRequests, ("listener",))

		while(True): #Eternamente lendo mensagens (Pront)
			print("Informe o nome do arquivo.")
			arquivo = input() #Lemos uma nova mensagem
			if(arquivo != ""):
				arq = open(arquivo,'r')
				mensagem = arq.read();

				msgNum = ""

				nomeArquivo = nome + "-"+ str(ultimaMsg) + ".serv"
				arquivo = open(nomeArquivo,'w+')
				arquivo.write(mensagem)
				arquivo.close()

				try:
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.connect((serverAddress, serverPort))
					sock.sendall(bytes(str("0;" + str(listenerPort)), "utf-8")) #Informamos ao servidor que uma nova mensagem foi criada
					msgNum = str(sock.recv(1024), "utf-8") #Ele nos retorna o número de mensagem que registrou
				finally:
					sock.close()

				if(msgNum == ""):
					print("Erro no envio, tente novamente")
				else:
					msgNum = int(msgNum)
					temp = len(mensagens) - 1
					if(msgNum > temp):
						cont = temp
						while(True):
							cont = cont +1
							if(cont < msgNum):
								mensagens.append("")
							else:
								mensagens.append(mensagem)
								break
					else:
						mensagens[msgNum] = mensagem

except KeyboardInterrupt:
	print("\nExecução terminada")
