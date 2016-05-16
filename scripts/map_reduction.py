#!/usr/bin/env python
''' Takes global /map and returns surrounding local /nav_map'''
from numpy import array
import rospy
from sensor_msgs.msg import PointCloud
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Pose
from std_msgs.msg import Bool, Int16

def occ_grid_cb(data):
    global p,ready,first
    rospy.loginfo("occ_grid_cb() /ready_for_wps: %s",str(ready))
    if not ready.data:
	return
    nav_map = OccupancyGrid()
    w,h = data.info.width,data.info.height
    pt = data.data
    p = array(pt).reshape(w,h)#.T #<-- Transposes
    if not 'grid_loc' in globals():
        return
    x,y  = grid_loc.position.x, grid_loc.position.y
    nav_map.info = data.info
    if not 'size' in globals():
	size = 64
    if 'rtl' in globals() and rtl:
        ##Intelligently set mapsize, scale map, and send waypoints to home
	pass
    nav_map.info.width = size
    nav_map.info.height = size
    tmp_map = p[int(x)-size/2:int(x)+size/2,int(y)-size/2:int(y)+size/2]
    if first:
        tmp_map[:size/4,:] = 100
    nav_map.data = tmp_map.flatten()
    nav_map_pub.publish(nav_map)

def set_ready(data):
    global ready
    ready.data = data.data
    rospy.loginfo("set_ready() /ready_for_wps: %s",str(ready))

def set_rtl(data):
    global rtl
    rtl = data.data

def set_first(data):
    global first
    first = data.data

def get_curr_grid(data):
    global grid_loc
    grid_loc = data

def subs():
    rospy.init_node('UAV_nav_map')
    rospy.Subscriber('/gridout',Pose,get_curr_grid)
    rospy.Subscriber('/map',OccupancyGrid,occ_grid_cb)
    rospy.Subscriber('/ready_for_wps',Bool,set_ready)
    rospy.Subscriber('/first_wps',Bool,set_first)
    rospy.spin()
    

if __name__ == "__main__":
    global x,y,p,grid_loc,ready,rtl,first
    first = False
    rtl = False
    ready = Bool()
    ready.data = False
    x, y = 0, 0
    nav_map_pub = rospy.Publisher('nav_map',OccupancyGrid,queue_size=2)
    subs()
