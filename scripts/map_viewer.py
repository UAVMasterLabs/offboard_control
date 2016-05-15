#!/usr/bin/env python
import rospy, time
from numpy import array
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Pose
from offboard.msg import Waypoints

def print_map(data):
	data = data.data
	data = array(data).reshape(64,64)
	data[32,32] = 2
	while not 'x_wps' in globals():
		time.sleep(0.01)
	for i in range(len(x_wps)):
		data[x_wps[i],y_wps[i]] = 3
	swap = {0:' ',-1:'o',100:'*',2:'R',3:'+'}
	map = ''.join([swap[x] if i%64 else '\n'+swap[x] for i,x in enumerate(data.T.flatten())])
	print map	

def set_wps(data):
	global x_wps,y_wps
	x_wps = data.x
	y_wps = data.y

def subs():
	rospy.init_node('blah')
	rospy.Subscriber('/nav_map',OccupancyGrid,print_map)
	rospy.Subscriber('/next_wps',Waypoints,set_wps)
	rospy.spin()

subs()
