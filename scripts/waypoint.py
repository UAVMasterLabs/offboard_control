#!/usr/bin/env python
from __future__ import division
import rospy
from numpy import *
from geometry_msgs.msg import PoseStamped, TwistStamped
from tf.transformations import euler_from_quaternion as efq

def transform(pose):
	pose = pose.pose
	pos = pose.position
	orient = pose.orientation
	# Simple rotations from ENU to NED... ish
	tfpos = array([pos.y,pos.x,-pos.z])
	tforient = efq([orient.x,orient.y,orient.z,orient.w])
	# Transform from quat to euler happens in ENU frame.
	# Rotate to match NED
	tforient = array([-tforient[2],tforient[0],tforient[1]])

	# Desired position. This should be read in from a file, or better
	# yet. should come from a subscription to a topic somehow. Still learning...
	des_pos = array([0,0,-1.5])
	pos_err = tfpos-des_pos
	vel_set(pos_err)

def vel_set(err):
	pub = rospy.Publisher('/mavros/setpoint_velocity/cmd_vel',TwistStamped,queue_size=10)
	vel = TwistStamped()
	vel.header.stamp = rospy.Time.now()
	err = [i for i in err if i <= 1 else 1]
	x,y,z = err
	vel.twist.linear.x = x
	vel.twist.linear.y = y
	vel.twist.linear.z = z
	pub.publish(vel)

def position():
	rospy.init_node('waypoint_getter', anonymous=True)
	rospy.Subscriber('/mavros/mocap/pose',PoseStamped,transform)
	rospy.spin()

if __name__ == '__main__':
	position()
