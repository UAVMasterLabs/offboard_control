#!/usr/bin/env python
'''Can be run with
>$python map_viewer.py
OR
>$rosrun offboard map_viewer.py
NOTE: This only prints out a map when nav_map receives the go ahead from
the /ready_for_wps topic. /reday_for_wps tells map_reduction.py to reduce
the map, map_reduction.py publishes /nav_map, path_finder.py subscribes to
/nav_map and gets a path (usually a single line-of-sight waypoint) from 
sentel's code, and then traj_set.py takes the path, translates it into
something usable and publishes setpoints to the pixhawk.
map_viewer.py Map legend:
" " = Explored, Unobstructed
"*" = Explored, Obstructed
"o" = Unexplored
"R" = Robot currrent location
"+" = Waypoints (obviously in grid locations)'''
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
	map = ''.join([swap[x] if i%64 else '\n'+swap[x] for i,x in enumerate(data.flatten())])
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
