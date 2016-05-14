#!/usr/bin/env python
# Code copyright by Sentel and Mohammad Sarim, 04/28/2016.

import rospy
from py4j.java_gateway import JavaGateway, Py4JNetworkError
from py4j.java_collections import SetConverter, MapConverter, ListConverter
import sys
import time
import os
from nav_msgs.msg import OccupancyGrid
from std_msgs.msg import Int8MultiArray
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from offboard.msg import Waypoints

def occ_grid_cb(OccupancyGrid):
	'''This function is called everytime new map data is published
	to the /map topic. Here we pass the dataon to be processed as
	a tunnel for path finding'''
	mapdata = OccupancyGrid
	genTunnel(mapdata)

def genTunnel(mapdata):
	'''Takes /map topic data and generates a tunnel in the correct
	format for the Sentel navigation engine. I see no easy way
	modifying explorer as a global as this must return void. The
	only other possibility would be to publish this to a new topic
	and path plan in another subscription service. We will do this
	if we notice data is getting corrupted or the state of explorer
	is unclear'''
	global explorer,ways,pubway
	print('I have the nav_map')
	size = mapdata.info.width
	data = mapdata.data
	explorer.initializeArray(size)
	explorer.importHectorList(ListConverter().convert(data,gateway._gateway_client),1)
	shortestdistance = 3
	maxrange = 40

	p = explorer.findClosestFrontier(size/2,size/2,maxrange,shortestdistance)
	ways = Waypoints()
	x_ways, y_ways = [], []
	for pp in p:
		x_ways.append(int(pp.getX()))  #Possible tranpose, but map_viewer works currently
		y_ways.append(int(pp.getY()))
	ways.x = x_ways
	ways.y = y_ways
	pubway.publish(ways) #publishing x,y gridpoints



def talker(size):
	'''This is the main function of the whole script. Here we set up all of
	publishers and subscribers. In short, subscribe to the map and attach it
	to genTunnel (via callback()). explorer is updated in the process and we
	can then call the navigation engine functions on it. A path is returned
	and the next waypoint is published on the /next_wp topic'''
	global pubway
	mapdata = Int8MultiArray()	
	rospy.init_node('talker', anonymous=True)
	pub = rospy.Publisher('mapprob', Int8MultiArray, queue_size=10)
	pubway = rospy.Publisher('next_wps', Waypoints, queue_size=10)
	rospy.Subscriber("nav_map", OccupancyGrid, occ_grid_cb)
	rospy.spin()


if __name__ == '__main__':
	global explorer

	#instantiate the java gateway using py4j. This requires that py4j be installed
	#using sudo pip install py4j. navigation engine must be up and running using
	#java -jar navengine.jar
	gateway = JavaGateway()
	explorer = gateway.entry_point

	#must intialize the navigation map in engine to be same size as the map that
	#is passed in. This can be called multiple times if size changes. Be sure to
	#recopy in all data after resizing since this initializes everything to unexplored
	#and unobstructed
	size = 64

	while True:
	#The roslaunch file does not guarantee any ordering of process startup
	#so I'm making the assumption that the time between now and the navengine
	#starting up is relatively short (and just catch the errors in the meantime)
	#If the navengine is not started, this will silently fail forever (bad).
		try:
			explorer.initializeArray(size)
		except Py4JNetworkError:
			rospy.loginfo('Waiting for navengine')
			continue
		else:
			break

	try:
		talker(size)
	except rospy.ROSInterruptException:
		pass
