import socketserver
import sys

mensagens = []
ultimaMsg = -1

def count(l):
    return sum(1+count(i) for i in l if isinstance(i,list))

class SenderHandler(socketserver.BaseRequestHandler):


	def handle(self):
		global mensagens
		global ultimaMsg
		self.data = self.request.recv(1024).strip()
		data = self.data.decode("utf-8")
		data = data.split(";")


		if(data[0] == "0"):  #Cliente informa que criou uma mensagem
		
			ultimaMsg = ultimaMsg + 1
			mensagens.append(str(self.client_address[0]) + ";" +  str(data[1])) #Guardamos o endereço e porta listener de quem criou a mensagem
			self.request.sendall(bytes(str(ultimaMsg), "utf-8")) #Retorna ao criador da mensagem o número da mensagem criada no servidor

		elif(data[0] == "1"): #Retorna endereço de quem possui a mensagem i
			'''
			Considerando que o request seja no formato '1;i', onde i é o
			número da mensagem requisitada pelo cliente
			'''
			if(len(mensagens) > int(data[1])):
				if(not isinstance(mensagens[int(data[1])], list)): #Verificamos se só existe um endereço com a mensagem i
					envio = str(mensagens[int(data[1])])
				else:
					envio = str(mensagens[int(data[1])][0])
			else:
				envio = str("0")

			self.request.sendall(bytes(envio, "utf-8"))

		elif(data[0] == "2"): #Cliente informa ao servidor que recebeu a mensagem i
			# Considerando que o formato do request é '2;i;client_listenerPort', onde i é a mensagem que o cliente agora possui

			#Guardamos o endereço do cliente que recebeu a mensagem
			if(not isinstance(mensagens[int(data[1])], list)): #Verificamos se só existe um endereço para a mensagem i

				mensagens[int(data[1])] = list((str(str(self.client_address[0]) + ";" + str(data[2])), mensagens[int(data[1])]))
			else:
				mensagens[int(data[1])].insert(0, str(str(self.client_address[0]) + ";" + str(data[2])))
		elif(data[0] == "3"): #Informa ao cliente o número da última mensagem registrada
			self.request.sendall(bytes(str(ultimaMsg), "utf-8"))

PORT = 8000
# Ouvir em todas as interfaces desta máquina
HOST = '0.0.0.0'

print("Iniciando servidor")
try:
	socketserver.TCPServer.allow_reuse_address = True
	server = socketserver.TCPServer((HOST, 8000), SenderHandler)
	server.serve_forever()

	#Fechar servidor com Ctrl+C
except KeyboardInterrupt:
	print("\nParando Servidor")
	server.server_close()
