#!/usr/bin.env python
import rospy
from nav_msgs.msg import OccupancyGrid
from nav_msgs.msg import MapMetaData
from geometry_msgs.msg import PoseStamped,Pose

global mapinfo, grid_pub
mapinfo = MapMetaData()

def set_orig(data):
	global mapinfo
	mapinfo = data

def update_pose(data):
	pose = data.pose
	curr_x = pose.position.x
	curr_y = pose.position.y
	print_grid_loc(curr_x,curr_y)

def print_grid_loc(x,y):
	global grid_pub
	grid_loc = Pose()
	orig_x = mapinfo.origin.position.x
	orig_y = mapinfo.origin.position.y
	res = mapinfo.resolution
	grid_loc.position.x = (x-orig_x)/res
	grid_loc.position.y = (y-orig_y)/res
#	print(grid_loc.position)
	grid_pub.publish(grid_loc)
	

def subs():
	global grid_pub
	rospy.init_node('printer')
	rospy.Subscriber('/map_metadata',MapMetaData,set_orig)
	rospy.Subscriber('/slam_out_pose',PoseStamped,update_pose)
	grid_pub = rospy.Publisher('gridout',Pose,queue_size=10)
	rospy.spin()

subs()
