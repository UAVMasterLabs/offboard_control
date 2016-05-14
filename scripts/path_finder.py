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
	'''for ind in range (0,size*size):
		y0 = divmod(ind,size)
		x = y0[1]
		y = y0[0]
		if mapdata.data[ind]==-1:
			explorer.addNode(y,x,False,False)
		else:
			if mapdata.data[ind]==100:
				explorer.addNode(y,x,True,True)
			else:
				explorer.addNode(y,x,True,False)'''
	explorer.initializeArray(size)
	explorer.importHectorList(ListConverter().convert(data,gateway._gateway_client),1)
	shortestdistance = 3
	maxrange = 40

	#get first move
	p = explorer.findClosestFrontier(size/2,size/2,maxrange,shortestdistance)
	ways = Waypoints()
	x_ways, y_ways = [], []
	for pp in p:
		x_ways.append(int(pp.getX()))
		y_ways.append(int(pp.getY()))
	ways.x = x_ways
	ways.y = y_ways
	pubway.publish(ways)



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

#	time.sleep(10)


	#shortest distance to consider and maximum range to use for navigation
	#these work for a 30 x 30 but for a larger obstacle map may need to be
	#larger. Some experimentation will be needed to find a good balance of
	#performance

#	shortestdistance = 3
#	maxrange = 40

	#get first move
#	p = explorer.findClosestFrontier(size/2,size/2,maxrange,shortestdistance)
#	last = False

	#while we still have moves and have not returned to home base navigate
	#around
#	while p is not None:
#		for pp in p:
#			#jva.awt.point uses floats so we cast back to integers here
#			way = Point()
#			x = int(pp.getX())
#			y = int(pp.getY())
#			way.x = x
#			way.y = y
#			n = explorer.getNode(x,y)
#			while not rospy.is_shutdown():
#				pubway.publish(way)
		#x_path,y_path = zip(*[(pp.getX(),pp,getY()) for pp in p])
	'''ways = PoseArray()
	for pp in p:
		way = Pose()
		way.position.x = int(pp.getX())
		way.position.y = int(pp.getY())
		ways.poses.append(way)
	print(len(ways.poses))
	pubway.publish(ways)'''
#		if last:
#			break

#get next path to explore wil return None if none found
#none found usually implies we've fully explored the space provided but
#may also mean that max range wasn't high enough or shortest distance to
#consider was too long

#		p = explorer.findClosestFrontier(way.position.x,way.position.y,maxrange,shortestdistance)

#		print p
#get path back home if no frontier was found to explore

#		if p is None and not last:
#			last = True
#			p = explorer.findPath(way.position.x,way.position.y,size,0,shortestdistance)

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

#	flag = 0

	try:
		talker(size)
	except rospy.ROSInterruptException:
		pass
