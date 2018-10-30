# -*- coding: utf-8 -*-
#follower
#cmd_vel,odom 
#Folow sombody and generate a new behavior
#turlebot
#./know/follower.py
#name
#controlo 
#active


######################################
# This file simulate a robot on ROS. #
# To use, you need to pass like      #
# argument the numnber of robot,     #
# like "./movingRobot 1"             #
######################################


from Controlo import Controlo
#ROS  imports
import rospy
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Quaternion
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool
from std_msgs.msg import String
import os
import random
import sys
import time
from math import tanh
#extra
from kobuki_msgs.msg import Sound
from kobuki_msgs.msg import ButtonEvent
from kobuki_msgs.msg import Led
####
from tf.transformations import euler_from_quaternion
import tf
import struct
from datetime import datetime
from sensor_msgs.msg import LaserScan
getTime = lambda: int(round(time.time() * 1000))

import math
RATE = 10

#real turtlebot
MAX_LIN = 0.15
MAX_ANG = 0.85
#simulated  turtlebot
#MAX_LIN = 0.6
#MAX_ANG = 0.5

global posicao
posicao = []
global distance
distance = None
global angle
angle = 0
#the minimal distance from the target
MIN_DIST = 70
#it will follow objects in this gap Min|Max
MAX_DIST = 200
global cont
cont =0

global cont_gen
cont_gen = 0
global posicao_cont
posicao_cont =0

global button_state
button_state = 0

def handle_buttons(bt):
	global button_state
	if bt.state == 1:
		button_state +=1

def gen_header():
	global cont_gen
	cont_gen+=1
	header = []
	header.append("#generated" + str (cont_gen)+"\n")
	header.append("#cmd_vel, base_pose_ground_truth"+"\n")
	header.append("#This is a generated model for turtlebot"+"\n")
	header.append("#turtlebot"+"\n")
	header.append("#./know/generated_behavior"+str(cont_gen)+".py"+"\n")
	header.append("#name"+"\n")
	header.append("#controlo"+"\n")
	header.append("#active"+"\n")
	return header
def handle_positions():
	global posicao
	value = "["
	for i in range (len (posicao)):
		if i == len (posicao)-1:
			value+= str(posicao[i])
		else:
			value+= str(posicao[i])+","
	value +="]"
	posicao = []
	return value
	
def gen_new_behavior():
	global cont_gen
	file = open ("./know/model.py", "r")
	model = file.readlines()
	file.close()
	header = gen_header()
	for i in range (0,8):
		model[i+1]=header[i] 
	model[96]= "points = " + handle_positions() + "\n"
	file = open ("./know/generated_behavior"+str(cont_gen)+".py", "wb")
	for i in model:
		file.write(i)
	file.close()

def get_button():
	pass

def get_scan(scan):
	global angle
	global distance
	temp = list (scan.ranges)
	for n, i in enumerate (temp):
		if math.isnan(i):
			temp[n] = 3
	for i in range (0,len(temp)):
		temp[i] = round (temp[i] * 100,1)
	distance = min(temp)
	angle = temp.index(distance)

def degrees(value):
	return (value*180)/math.pi#math.degrees(value)#((value* 180.0)/math.pi)

def get_pos(odom):
	global posicao
	global posicao_cont
	posicao_cont +=1
	if posicao_cont>40:
		posicao_cont = 0
		posicao.append(getxy(odom))

def getDegreesFromOdom(w):
	#TODO: HOW CONVERT DATA TO ANGLES
	q = [w.pose.pose.orientation.x,	w.pose.pose.orientation.y, w.pose.pose.orientation.z, w.pose.pose.orientation.w]       
        euler_angles = euler_from_quaternion(q, axes='sxyz')
	current_angle = euler_angles[2]
	if current_angle < 0:
		current_angle = 2 * math.pi + current_angle
	return degrees(current_angle)
		

def getxy (odom):
	return round (odom.pose.pose.position.x, 2), round ( odom.pose.pose.position.y,2), round (getDegreesFromOdom (odom),2)#degrees(yall)

#############
# ROS SETUP #
#############
#Became a node, using the arg to decide what the number of robot
global myId
myId = sys.argv[1].replace("robot_", "")
	
robot = sys.argv[1]#,sys.argv[2],sys.argv[3], sys.argv[4]
rospy.init_node("robot_"+str(robot)+"_folower")
finish = None
p = None

if False: #simulated robots
	rospy.Subscriber("/robot_0/odom", Odometry, get_pos)
	rospy.Subscriber("/robot_0/base_scan", LaserScan, get_scan)
	p = rospy.Publisher("/robot_0/cmd_vel", Twist)
else: # real robots
	rospy.Subscriber("/robot_0/odom", Odometry, get_pos)
	rospy.Subscriber("/robot_0/scan", LaserScan, get_scan)
	rospy.Subscriber("/robot_0/mobile_base/events/button", ButtonEvent, handle_buttons)
	p = rospy.Publisher("/robot_0/cmd_vel_mux/input/teleop", Twist)
	f = rospy.Publisher("/finish_f", String)
	w = rospy.Publisher("/working", String)
#	rospy.Subscriber("robot_0/mobile_base/events/button", String, get_button)
	psound = rospy.Publisher("/robot_0/mobile_base/commands/sound", Sound)


r = rospy.Rate(RATE) # 5hz

print "Iniciado o follower"
tempoInicial = getTime()
button = True
teste = 0
try:
	while not rospy.is_shutdown():#button:
		global button_state
		if button_state >= 1:
			teste +=1
			#starts to follow 
			v = Twist()
			v.linear.x = 0
			v.angular.z = 0
			global distance
			global angle
			if distance!=None and distance < MAX_DIST and (distance < MIN_DIST -5 or distance > MIN_DIST + 5):
#			print ("Distancia " + str (MAX_DIST-5) + " " + str (distance) + " "+ str(MAX_DIST + 5) )
#			if distance!=None and not ( distance > MAX_DIST- 5 or distance < MAX_DIST +5):
				v.angular.z = ((angle-320)/320.0)
				v.linear.x = tanh (5 * (distance - MIN_DIST)) * MAX_LIN
			else:
				v.linear.x = 0
			if abs(v.linear.x) < 0.01:
				v.linear.x = 0
			p.publish (v)
			if button_state >2:
				print "Gerando novo comportamento"
				gen_new_behavior()
				f.publish("foi")
				r.sleep()
				w.publish(True)
				r.sleep()
				print "new behavior generated sucessfully"
				sys.exit()
		
	r.sleep()

except Exception :
	raise	
	print ("Exception!\n")
