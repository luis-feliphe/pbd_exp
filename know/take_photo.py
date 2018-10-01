# -*- coding: utf-8 -*-
#take_photo
#cmd_vel, base_pose_ground_truth
#Takes photo from an obstacle
#turlebot
#./know/take_photo.py
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
####
from tf.transformations import euler_from_quaternion
import tf
import struct
from datetime import datetime
from sensor_msgs.msg import LaserScan
getTime = lambda: int(round(time.time() * 1000))

import math
RATE=6


global posicao
posicao = None


def degrees(value):
	return (value*180)/math.pi#math.degrees(value)#((value* 180.0)/math.pi)
def getpos(odom):
	global posicao
	posicao= odom

def hasDataToWalk():
	global posicao
	return posicao != None

def getDataFromRos():
	global posicao
	x, y, z = 0, 0 ,0
	mx, my, mz = getxy (posicao)
	return x, y , mx, my, mz

def getDegreesFromOdom(w):
	#TODO: HOW CONVERT DATA TO ANGLES
	q = [w.pose.pose.orientation.x,	w.pose.pose.orientation.y, w.pose.pose.orientation.z, w.pose.pose.orientation.w]       
        euler_angles = euler_from_quaternion(q, axes='sxyz')
	current_angle = euler_angles[2]
	if current_angle < 0:
		current_angle = 2 * math.pi + current_angle
	return degrees(current_angle)
		

def getxy (odom):
	return round (odom.pose.pose.position.x,2), round ( odom.pose.pose.position.y,2), round (getDegreesFromOdom (odom),2)#degrees(yall)

#############
# ROS SETUP #
#############
#Became a node, using the arg to decide what the number of robot
global myId
myId = sys.argv[1].replace("robot_", "")





robot = sys.argv[1]#,sys.argv[2],sys.argv[3], sys.argv[4]
rospy.init_node(str(robot)+"_gotoB")
rospy.Subscriber(robot+"/odom", Odometry, getpos)
finish = rospy.Publisher(robot+"/working", Bool)
p = rospy.Publisher(robot+"/cmd_vel_mux/input/teleop", Twist)

r = rospy.Rate(RATE) # 5hz


######################
# control stops ######
######################

#################
#   Main Loop   #
#################
u= 1.5#0.75/2
points = [(0, -2 * u)]
cont = 0
posInicialx=0
posInicialy=0

#Esperar resposta (verificar se estamos em A)

global inplace
inplace = None
def mypos(pos):
        global inplace
        place = ''.join(e for e in str(pos) if e.isalpha())
        if place.count("I") > 0:
                inplace = True
        else:
                inplace = False

rospy.Subscriber( robot+ "/place",  String , mypos)

os.system("python -W ignore ./know/findme.py "+ robot + " &")
while not inplace:
        if inplace == False:
		finish.publish(False)
		print '\033[91m' + "Not in place"
                sys.exit()
        r.sleep()









iteracoes = 1.0
tempoInicial = getTime()
try:
	algoritmo = Controlo()
	while not rospy.is_shutdown():
		if hasDataToWalk():
			x, y , mx, my, mz = getDataFromRos()
			t= Twist()
			x, y = points[cont]
			lin,ang  = algoritmo.start(str(myId),x, y, mx, my, mz)
			if (lin == 0 and ang == 0):
				cont= (cont + 1)%len (points)
				if (cont == 0):
					finish.publish(False)
					sys.exit()
			global saida
			t.angular.z = ang
			t.linear.x = lin
			p.publish(t)
		iteracoes += 1
		r.sleep()

except Exception :
	raise	
	print ("Exception!\n")

