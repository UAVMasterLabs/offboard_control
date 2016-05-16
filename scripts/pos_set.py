#!/usr/bin/env python
from __future__ import division
import rospy
from geometry_msgs.msg import PoseStamped
from tf.transformations import quaternion_from_euler as qfe
from mavros_msgs.msg import State,ExtendedState
from numpy import pi
import time

def set_id(data):
    global state_id
    if data.mode not in 'OFFBOARD':
	state_id = 1
    else:
	state_id = 2

def extend_set_id(data):
    global extend_set_id
    if data.landed_state == 2:
        extend_set_id = 'FLYING'
    else:
        extend_set_id = 'LANDED' 

def pos_set():
    global state_id, extend_set_id
    pub = rospy.Publisher('/mavros/setpoint_position/local', PoseStamped, queue_size=10)
    rospy.init_node('UAV_setpoint')
    rospy.Subscriber('/mavros/state',State,set_id)
    rospy.Subscriber('/mavros/extended_state',ExtendedState,extend_set_id)	
    rate = rospy.Rate(15)
    frame_id = 1
    extend_state_id = "FLYING"
    state_id = 1
    zdown = 0
    while not rospy.is_shutdown():
	if state_id is 1:  
       		pos = PoseStamped()
       		pos.header.stamp = rospy.Time.now()
       		pos.pose.position.x=0
       		pos.pose.position.y=0
		pos.pose.position.z=0
	        quat = qfe(0,0,pi/2)
	        pos.pose.orientation.w = quat[3]
	        pos.pose.orientation.x = quat[0]
	        pos.pose.orientation.y = quat[1]
	        pos.pose.orientation.z = quat[2]
	        pub.publish(pos)
	elif 1 < frame_id < 150:
       	        pos = PoseStamped()
       	        pos.header.stamp = rospy.Time.now()
       	        pos.pose.position.x=0
       	        pos.pose.position.y=0
       		pos.pose.position.z=0.50
                quat = qfe(0,0,pi/2)
       	        pos.pose.orientation.w = quat[3]
               	pos.pose.orientation.x = quat[0]
               	pos.pose.orientation.y = quat[1]
               	pos.pose.orientation.z = quat[2]
               	pub.publish(pos)
        elif 150 <= frame_id < 300:
                pos = PoseStamped()
                pos.header.stamp = rospy.Time.now()
                pos.pose.position.x=0
                pos.pose.position.y=1
                pos.pose.position.z=0.5
                quat = qfe(0,0,pi/2)
                pos.pose.orientation.w = quat[3]
                pos.pose.orientation.x = quat[0]
                pos.pose.orientation.y = quat[1]
                pos.pose.orientation.z = quat[2]
                pub.publish(pos)
	elif 300 <= frame_id <450:
                pos = PoseStamped()
                pos.header.stamp = rospy.Time.now()
                pos.pose.position.x=0
                pos.pose.position.y=0
                pos.pose.position.z=0.5
                quat = qfe(0,0,pi/2)
                pos.pose.orientation.w = quat[3]
                pos.pose.orientation.x = quat[0]   
                pos.pose.orientation.y = quat[1]
                pos.pose.orientation.z = quat[2]
		pub.publish(pos)
	elif 450 <= frame_id <550:
                pos = PoseStamped()
                pos.header.stamp = rospy.Time.now()
                pos.pose.position.x=0
                pos.pose.position.y=0
                pos.pose.position.z=0.5
                quat = qfe(0,0,pi/2)
                pos.pose.orientation.w = quat[3]
                pos.pose.orientation.x = quat[0]   
                pos.pose.orientation.y = quat[1]
                pos.pose.orientation.z = quat[2]
                pub.publish(pos)
	else:
		if extend_state_id is 'FLYING':
			zdown -= 1		
       	        pos = PoseStamped()
       	        pos.header.stamp = rospy.Time.now()
       	        pos.pose.position.x=0
       	        pos.pose.position.y=0
       	        pos.pose.position.z=zdown
       	        quat = qfe(0,0,pi/2)
       	        pos.pose.orientation.w = quat[3]
       	        pos.pose.orientation.x = quat[0]
       	        pos.pose.orientation.y = quat[1]
       	        pos.pose.orientation.z = quat[2]
       	        pub.publish(pos)
		if extend_state_id is 'LANDED':
			rospy.set_param('mavsafety','disarm')
			break
	if state_id is 2:
		frame_id += 1
	rate.sleep()

if __name__ == '__main__':
	global state_id
	try:
		pos_set()
	except rospy.ROSInterruptException:
		pass
