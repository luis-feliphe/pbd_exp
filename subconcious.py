# -*- coding: utf-8 -*-

"""
This file is respnsible to manage how a robot can learn and teach
"""

__author__="LF"
__date__="09/06/2016"
__version__="0.1"

from knowledge import Knowledge
import os
import random 
import sys
import time
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from std_msgs.msg import Bool 
getTime = lambda: int(round(time.time()))
global box 
box = False


DEBUG = True

def log (string):
	if DEBUG==True:
		print '\033[93m' + "\n "+ str(getTime()) + ":" + str (string) + '\033[0m'

class Subconcious:


#patrol, Controlo, follower, gotoxy, avoidance, take_photo


	def __init__(self):
		''' Settings '''
		self.rule = 0
		os.system("rm ./know/Controlo.pyc")
		os.system("rm ./knowledge.pyc")
		#if im robot 1
		if sys.argv[1].count ("0")>0:
			self.rule = 1
#			print "Im robot 1"
#			os.system("rm ./know/take_photo.py")
		#if Im robot 2
		elif sys.argv[1].count ("1")>0:
			print "Im robot 2"
			self.rule = 2
#			os.system("rm ./know/take_photo.py")
#			os.system("rm ./know/follower.py")
#			os.system("rm ./know/patrol.py")
#			os.system("rm ./know/gotoxy.py")
			os.system("rm ./know/*")
		#if Im robot 3
		elif sys.argv[1].count ("2")>0:
			self.rule = 3
			print "Im robot 3"
#			os.system("rm ./know/Controlo.py")
#			os.system("rm ./know/gotoxy.py")
#			os.system("rm ./know/patrol.py")
#			os.system("rm ./know/follower.py")
#			os.system("rm ./know/move_around.py")

		#variables
		self.working = False
		self.knowledge = []
		self.shared_knowledge= []
		rospy.init_node('robot_concious_'+ sys.argv[1])
		self.att={"name" : sys.argv[1], "None": ""}

		self.pknow = rospy.Publisher('/knowledge', String)
		self.pask = rospy.Publisher('/ask_knowledge', String)
		self.finish = rospy.Publisher(sys.argv[1]+ "/working" , Bool)

		rospy.Subscriber ("/knowledge", String, self.receive_knowledge)
		rospy.Subscriber ("/finish_f", String, self.isbox)
		rospy.Subscriber ("/ask_knowledge", String, self.handle_requests)
		rospy.Subscriber (sys.argv[1] + "/working", Bool, self.worker_process)

		self.r = rospy.Rate (10)	
		self.learn_from_file()
		self.initialTime = getTime()
		self.log = open ( "log.txt", 'a+')
		self.last_shared = []
		self.main()

#
#		self.log.write(str(getTime()) + ":"+ str(string) + "\n" )
		#variables
#		self.working = False
#		self.knowledge = []
#		self.shared_knowledge= []
#		rospy.init_node('robot_concious_'+ sys.argv[1])
#		self.att={"name" : sys.argv[1], "None": ""}
#		self.pknow = rospy.Publisher('knowledge', String)
#		self.pask = rospy.Publisher('ask_knowledge', String)
#		self.finish = rospy.Publisher(sys.argv[1]+ "/working" , Bool)
#		rospy.Subscriber ("knowledge", String, self.receive_knowledge)
#		rospy.Subscriber ("ask_knowledge", String, self.handle_requests)
#		rospy.Subscriber (sys.argv[1] + "/working", Bool, self.worker_process)
#		self.r = rospy.Rate (10)	
#		self.learn_from_file()
#		self.initialTime = getTime()
#		self.log = None
#		self.main()

	def addInLog(self,string):
		self.log = open ( "log.txt", 'a+')
		self.log.write(str(getTime()- self.initialTime) + ":"+ str(string) + "\n" )
		self.log.close()

	def __exit__(self, exc_type, exc_value, traceback):
		print (self.log)

	def main(self):
		'''Here is the main loop, a brain never stops '''
		cont = 0
		while not rospy.is_shutdown():
			cont += 1
			if not self.working:
				if (self.rule == 1):
					if not box:
						self.run("follower")
					else:
						print "entrou"
						self.learn_from_file()
						self.share_knowledge ("generated1")
				elif (self.rule == 2):
					self.run ("generated1")
				elif (self.rule==3):
					self.run ("gotoxy")
				#if len (self.shared_knowledge ) <= len (self.knowledge):
#				work = random.randint (1,2) # 1 - compartilha qualquer  conhecimento;2 - realiza uma tarefa; 3 - pede para aprender alguma coisa; 
#				if work <2:
#					if (len (self.last_shared) < len (self.knowledge)):
#						name = random.choice(self.knowledge)
#						while str(name.name) in self.last_shared:
#							name=random.choice(self.knowledge)
#						self.share_knowledge(name.name)
#						
#					else:
#						self.last_shared = []
#						self.share_knowledge("any")
#				elif work ==2:
#					self.run("any")
			self.r.sleep()
			#Eu tenho objetivo?
			#Eu devo aprender algo?
			#Sim=publico pedindo algo| escuto algo
			#Treino o que aprendi (faco alguma coisa

	def worker_process (self, value):
		print "Working" + str (value)
		self.working  = False 

	def organize_args (self, task):
		args = ""
		for attribute in task.att:
			if (attribute != "none"):
				args = args +  " " + self.att[attribute]
		return args

	def run (self, task):
		''' Run some task - Executa a tarefa '''
		if len (self.knowledge) == 0:
			return 
		elif (task == "any" or self.has (task)):
			if task == "any":
				temp = random.choice (self.knowledge)
			else:
				temp = self.has(task)
			# check if task is passive or active
			if (temp.type == "passive"):
				log ( "Passive knowledge " + str (temp.name) + " " +str (temp.type) )
				return
			# check if task have all dependencies
			ok = 0
			resting_dep = temp.dependences
			my_know = []
			missing_dep = []
			for i in self.knowledge:
				my_know.append(i.name)
			for i in resting_dep:
				if i not in my_know:
					missing_dep.append(i)
			if len (missing_dep) > 0 :
				log ("Missing Dependences: " + str (missing_dep)+ ", asking for one of them")
				request = str(self.rule) + " "+ str (missing_dep[0])
				self.pask.publish(request)	
				return 
			args = self.organize_args (temp)
			log ("Starting to run : " + str (temp.name))# + str (temp.type))
			os.system("python -W ignore "+ temp.arquivo+" " + args + " &")
			self.working = True
		else:
#			performed = False
#			for i in self.knowledge:
#				if i.name == task:
#					args = self.organize_args (i)
#					os.system("python -W ignore "+ i.arquivo + " " + args + " &")
#					performed= True
#					self.working = True
#			if not performed:
			request = str(self.rule) + " " + str(task)
			print "impossible to find this task, asking for it: " + str (request)
			self.pask.publish(request)
				



	def learn_from_file(self):
		self.knowledge = []
		''' It search for knowledge in directory, if exists it is loaded - Procura conhecimentos no diretório, se existir são carregados'''
		log ("charging knowledge from files")
		import glob
		files = glob.glob("./know/*")
		for file in files:
			data = open (file, "r")
			data = data.readlines()

			nome = data[1].replace("#", "").replace ("\n","")
			print nome
			topicos = data[2].replace("#", "").replace ("\n","")
			descricao = data [3].replace("#", "").replace ("\n","")
			modelo = data[4].replace("#", "").replace ("\n","")
			endereco = file
			atributos = data[6].replace("#", "").replace ("\n","").split()
			dependencias = data[7].replace("#", "").replace ("\n","").replace(",", "").split()
			for dep in dependencias:
				dep = dep.replace(",", "").replace(" ", "")
			tipoDeTarefa = data[8].replace("#", "").replace ("\n","").split()
			if len (tipoDeTarefa ) > 0 :
				tipoDeTarefa = tipoDeTarefa.pop()
			else:
				tipoDeTarefa = "passive"
			#print (type (tipoDeTarefa))
			know = Knowledge ( nome, topicos, descricao, modelo , endereco, atributos,dependencias, tipoDeTarefa )
			self.knowledge.append(know)

	def isbox(self, knowledge):
		print "Recebeu"
		global box
		self.working = False
		box = True
	def receive_knowledge(self, knowledge):
		''' Callback: It receives knowledges from topic and save it in files - Recebe conhecimento e o salva em arquivos'''
		data = str(knowledge.data).split("\n")
		if self.has(data[1].replace("#","").replace("\n", "")):
			#log ("I already have this knowledge: " + str(data[1]))
			return
		nome = data[1].replace("#", "").replace ("\n","")
		topicos = data[2].replace("#", "").replace ("\n","")
		descricao = data [3].replace("#", "").replace ("\n","")
		modelo = data[4].replace("#", "").replace ("\n","")
		endereco = data[5].replace("#", "").replace ("\n","")
		atributos = data[6].replace("#", "").replace ("\n","").split()
		dependencias = data[7].replace("#", "").replace ("\n","").replace(",", "").split()
		for dep in dependencias:
			dep = dep.replace(",", "").replace(" ", "")
		tipoDeTarefa = data[8].replace("#", "").replace ("\n","").split()
		if len (tipoDeTarefa ) > 0 :
			tipoDeTarefa = tipoDeTarefa.pop()
		else:
			tipoDeTarefa = "passive"
	
		know = Knowledge ( nome, topicos, descricao, modelo , endereco, atributos, dependencias, tipoDeTarefa)

		file = open (data[5].replace("#","").replace("\n", ""), "wb")
		for i in data:
			file.write(i+"\n")
		self.knowledge.append(know)
		file.close()
		print ('\033[94m' + "I learn!" + str (data[1]) )
		self.addInLog("Learn " + str(data[1]))


	def handle_requests(self, ask):
		''' You are listening requests for knowledge, if you have it, you will share  - Esta função administra pedidos de ensino de conhecimento'''
		behavior = str(ask).split(" ")[2].replace(" ","")
		if int (str(ask).split(" ")[1]) == self.rule:
			return False #asking for myself
		if self.has(behavior) != None:
			self.share_knowledge(behavior)
			return True
		return False


	def share_knowledge(self, know):
		''' You decide send knowledge to comunity'''
#		log ("I decided share knowledge with my team")
		print "compartilhando comportamento " + str (know)
		temp = None
		resp= ""
		if len (self.knowledge) == 0: 
			return False
		elif(know == "any"):
			temp = random.choice(self.knowledge)
		else: 
			temp = self.has(know)
		if temp != None :
			self.addInLog("teaching " + str (temp.name))
			self.last_shared.append(str(temp.name))
			self.shared_knowledge.append(temp.name)
			file = open (temp.arquivo, "r")
			data = file.readlines()
			file.close()
			for line in data:
				resp = resp+line
			self.pknow.publish(resp)
			return 
		print "Not shared, I dont have it"

	def has(self, knowledge):
		for task in self.knowledge:
			if task.name == knowledge:
				return task
		return None


x = Subconcious()
