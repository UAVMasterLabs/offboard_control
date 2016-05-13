#!/usr/biin/env python
import rospy
from numpy import array
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Pose
from offboard.msg import Waypoints

def print_map(data):
	data = data.data
	data = array(data).reshape(64,64)
	if curr_grid in globals():
		data[int(curr_grid.position.x),int(curr_grid.position.y)] = 2
	if x_wps in globals():
		for i in len(x_wps):
			data[x_wps[i],y_wps[i]] = 3
	swap = {0:' ',-1:'o',100:'*',2:'^',3:'+'}
	map = ''.join([swap[x] if i%64 else '\n'+swap[x] for i,x in enumerate(data.flatten())])
	

def set_grid(data):
	global curr_grid
	curr_grid = data

def set_wps(data):
	global x_wps,y_wps
	x_wps = data.x
	y_wps = data.y

def sub():
	rospy.Subscriber('/gridout',Pose,set_grid)
	rospy.Subscriber('/nav_map',OccupancyGrid,print_map)
	rospy.Subscriber('/next_wps',Waypoints,set_wps)


subs()
