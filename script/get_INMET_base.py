#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import ast
from Estacao import *


def exportFileCSV(dados, file_name):

	try:
		f = open(file_name, "w")
		
		for i in range(len(dados)):
			f.write(dados[i]+"\n")

		f.close()
	except IOError:
		cookie = {}
		print "** ERROR: Erro ao abrir o arquivo %s **" % (file_name)
		return False

	return True

def getConsulta(session, url):
	response = session.get(url)

	text = response.content

	if(not("--------------------" in text)):
		return False

	text_splited = text.split("--------------------")
	descricao = text_splited[2]
	descricao_splited = descricao.split("\n")
	descricao_splited = descricao_splited[1:(len(descricao_splited)-1)]
	
	desc_name = descricao_splited[0].split(":", 1)[1].strip()
	desc_lat = descricao_splited[1].split(":", 1)[1].strip()
	desc_lng = descricao_splited[2].split(":", 1)[1].strip()
	desc_alt = descricao_splited[3].split(":", 1)[1].strip()
	desc_sit = descricao_splited[4].split(" ")[1].strip()
	desc_op_date = descricao_splited[5].split(":", 1)[1].strip()
	data_consulta = descricao_splited[6].split(":", 1)[1].strip()

	estacao_atual = Estacao(desc_name, desc_lat, desc_lng, desc_alt, desc_sit, desc_op_date)
	
	dados = text_splited[4]
	dados = dados.replace(";", ",")
	dados_splited = dados.split("\n")
	dados_splited = dados_splited[1:(len(dados_splited)-1)]

	#print estacao_atual

	#print "\n"

	#Definir o cabeçalho
	#dados_splited[0] = estacao_atual.getHead()+",data,hora,temp_comp_media,umidade_relativa_media,velocidade_vento_media"
	#print "%s" % dados_splited[0]

	dados_final = []
	for i in range(1, len(dados_splited)):
		#começa no indice 6 para retirar o código da estação que ja se repete na estação. Melhorar isso depois
		dados_final.append(estacao_atual.toCsvRow()+","+dados_splited[i][6:len(dados_splited[i])-1])
		#print "%s" % dados_splited[i]

	return dados_final
	

def getCookieFile(file_name):
	try:
		f = open(file_name)
		cookie = f.readline()
		if len(cookie) > 0:
			cookie = ast.literal_eval(cookie)
		else:
			cookie = {}
		f.close()
	except IOError:
		cookie = {}
		print "** ERROR: Erro ao abrir o arquivo %s **" % (file_name)

	return cookie

def setCookieFile(file_name, cookie):
	f = open(file_name, "w")
	f.write(cookie.__str__())
	f.close()

def checkSessionCookie(session):
	#URL de checagem para ver se esta logado
	url = 'http://www.inmet.gov.br/projetos/rede/pesquisa/mapas_mensal_sem.php'
	response = session.post(url)
	if not('<input type="text" size=51 maxlength=50 name="mCod"' in response.content):
		return True
	else:
		return False

def login(session):
	cookie_file = 'session_cookie.txt'
	cookie = getCookieFile(cookie_file)
	session.cookies = requests.utils.cookiejar_from_dict(cookie)

	# check if cookie from file is OK
	if(checkSessionCookie(session)):
		return True
	
	#IF NOT OK, then ask to user
	data = {}
	data['mCod'] = raw_input("Login: ")
	data['mSenha'] = raw_input("Password: ")
	response = session.post('http://www.inmet.gov.br/projetos/rede/pesquisa/inicio.php', data)
	
	#IF OK then return true, else FALSE
	if(checkSessionCookie(session)):
		#grava a nova cookie no arquivo
		setCookieFile(cookie_file, session.cookies.get_dict())
		return True
	
	print "\n Não foi possivel efetuar o Login. Tenha certeza de que o Usuário e senha estão corretos"

	return False


def main():

	
	session = requests.Session()
	
	logado = login(session)
	
	if logado:
		
		f = open("../dados/station_numbers.txt")
		station_numbers = f.readlines()
		data = []
		cont,contOK,contERROR = 0,0,0

		#head
		data.append(Estacao.head+",data,hora,temp_comp_media,umidade_relativa_media,velocidade_vento_media")

		for station in station_numbers:
			cont+=1
			station = station.replace("\n", "")
		
			url = "http://www.inmet.gov.br/projetos/rede/pesquisa/gera_serie_txt.php?&mRelEstacao="+station+"&btnProcesso=serie&mRelDtInicio=01/01/2016&mRelDtFim=01/08/2016&mAtributos=,,,,,,,,,,,,,1,1,1,"
			consulta = getConsulta(session, url)
			if type(consulta) is list:
				contOK+=1
				print str(cont)+" - "+str(station)+"\t[OK]"
				data = data+consulta
			else:
				contERROR+=1
				print str(cont)+" - "+str(station)+"\t[ERROR]"

		file_name = raw_input("Informe o nome do arquivo para exportação [Deixe em branco se não quer exportar]:")
		if(len(file_name)>0):
			exportFileCSV(data, file_name)

		print "\n\nTotal: "+str(cont)
		print "OK: "+str(contOK)
		print "ERROR: "+str(contERROR)
		print "Total de registros:"+str(len(data)-1)


if __name__ == '__main__':
	main()