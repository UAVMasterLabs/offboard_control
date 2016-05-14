#!/usr/bin/env python
from numpy import array
import rospy
from sensor_msgs.msg import PointCloud
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Pose
from std_msgs.msg import Bool

def occ_grid_cb(data):
    global p,ready
    if not ready:
	return
    nav_map = OccupancyGrid()
    w,h = data.info.width,data.info.height
    pt = data.data
    p = array(pt).reshape(w,h)
    if not 'grid_loc' in globals():
        return
    x,y  = grid_loc.position.x, grid_loc.position.y
    nav_map.info = data.info
    nav_map.info.width = 64
    nav_map.info.height = 64
    print(p.shape)
    nav_map.data = p[int(x)-32:int(x)+32,int(y)-32:int(y)+32].flatten()
    nav_map_pub.publish(nav_map)

def set_ready(data):
    global ready
    ready = data.data

def get_curr_grid(data):
    global grid_loc
    grid_loc = data

def subs():
    rospy.init_node('UAV_nav_map')
    rospy.Subscriber('/gridout',Pose,get_curr_grid)
    rospy.Subscriber('/nav_map',OccupancyGrid,occ_grid_cb)
    rospy.Subscriber('/ready_for_wps',Bool,set_ready)
    rospy.spin()
    
def RealtimePlotter2(arg):
    global p,grid_loc
    print p.shape,p.max(),p.min()


if __name__ == "__main__":
    global x,y,p,grid_loc,ready
    ready = Bool()
    ready.data = False
    x, y = 0, 0
    nav_map_pub = rospy.Publisher('nav_map',OccupancyGrid,queue_size=2)
    subs()
