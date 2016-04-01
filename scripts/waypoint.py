#!/usr/bin/env python
from __future__ import division
import rospy
from numpy import *
from geometry_msgs.msg import PoseStamped, TwistStamped
from tf.transformations import euler_from_quaternion as efq

def transform(PoseStamped):
	pose = PoseStamped.pose
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
	pos_err = des_pos - tfpos
	
	# Keep yaw turned towards +x
	des_yaw = 0
	yaw_err = des_yaw - tforient[0]

	vel_set(pos_err,yaw_err)

def vel_set(pos_err,yaw_err):
	pub = rospy.Publisher('/mavros/setpoint_velocity/cmd_vel',TwistStamped,queue_size=10)
	vel = TwistStamped()
	vel.header.stamp = rospy.Time.now()
	err = [i if abs(i)<=0.5 else i/(abs(i)*2) for i in pos_err]
	x,y,z = err
	vel.twist.linear.x = x
	vel.twist.linear.y = y
	vel.twist.linear.z = z
	yaw_err = yaw_err if abs(yaw_err)<=0.5 else yaw_err/abs(yaw_err*2)
	vel.twist.angular.z = yaw_err
	print err,yaw_err
	pub.publish(vel)

def position():
	rospy.init_node('waypoint_getter', anonymous=True)
	rospy.Subscriber('/mavros/mocap/pose',PoseStamped,transform)
	rospy.spin()

if __name__ == '__main__':
	position()
