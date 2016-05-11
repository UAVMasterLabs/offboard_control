#!/usr/bin/env python
from __future__ import division
import rospy
from geometry_msgs.msg import PoseStamped, PoseArray
from tf.transformations import quaternion_from_euler as qfe
from numpy import pi

def setpoints(data):
	global next_wp
	x_dist,y_dist = [],[]
	num_wps = len(data.poses)
	print(data.poses)
#	rospy.loginfo('%f,'*num_wps,data.poses)
#	print(type(data.poses[0].position.x))
	for pose in data.poses:
#		if not pose.position.x is None or pose.position.y is None:
		x_dist.append(pose.position.x - 32)*0.05
		y_dist.append(pose.position.y - 32)*0.05
	x_wps = [curr_x+x for x in x_dist]
	y_wps = [curr_y+y for y in y_dist]
	epsilon = 0.05
#	while abs(x_wps[0] - curr_x) > epsilon or abs(y_wps[0] - curr_y) > epsilon :
	next_wp.pose.position.x = x_wps[0]
	next_wp.pose.position.y = y_wps[0]
			

def set_curr(data):
	global curr_x, curr_y
	curr_x,curr_y = data.pose.position.x, data.pose.position.y


def wp_pub_sub():
	global curr_x,curr_y,next_wp
	next_wp.pose.position.z = 0.5
	rospy.init_node('UAV_setpoint',log_level=rospy.DEBUG,anonymous=True)
	rospy.Subscriber('next_wps',PoseArray,setpoints)
	rospy.Subscriber('slam_out_pose',PoseStamped,set_curr)
	rate = rospy.Rate(15)
	wp_pub = rospy.Publisher('/mavros/setpoint_position/local', PoseStamped, queue_size=10)
	while not rospy.is_shutdown():
		pos = PoseStamped()
		pos.header.stamp = rospy.Time.now()
		pos.pose.position.x = next_wp.pose.position.x
		pos.pose.position.y = next_wp.pose.position.y
#		pos.pose.position.z = next_wp.pose.position.z
		pos.pose.position.z = 0.75
		quat = qfe(0,0,pi/2)
		pos.pose.orientation.w = quat[3]
		pos.pose.orientation.x = quat[0]
		pos.pose.orientation.y = quat[1]
		pos.pose.orientation.z = quat[2]
		wp_pub.publish(pos)
		rate.sleep()


if __name__ == '__main__':
	global curr_x,curr_y,next_wp
	next_wp = PoseStamped()
	try:
		wp_pub_sub()
	except rospy.ROSInterruptException:
		pass
