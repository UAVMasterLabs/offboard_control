#!/usr/bin/env python
from __future__ import division
import rospy, time
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Bool
from offboard.msg import Waypoints
from tf.transformations import quaternion_from_euler as qfe
from tf.transformations import euler_from_quaternion as efq
from numpy import pi


def setpoints(data):
	global next_wp, ready_pub,spin
	ready_pub.publish(False)
	x_dist,y_dist = [],[]
	x_ways = data.x
	y_ways = data.y
	num_wps = len(x_ways)
	for i in range(num_wps):
		x_dist.append((y_ways[i] - 32.0)*0.05)
		y_dist.append(-(x_ways[i] - 32.0)*0.05)
	x_wps = [curr_x+x for x in x_dist]
	y_wps = [curr_y+y for y in y_dist]
	epsilon = 0.025
	for i in range(num_wps):
		dx = abs(x_wps[i] - curr_x)
		dy = abs(y_wps[i] - curr_y)
		rospy.loginfo("dx: %s\ndy: %s",str(dx),str(dy))
		while dx > epsilon or dy > epsilon :
			next_wp.pose.position.x = x_wps[i]
			next_wp.pose.position.y = y_wps[i]
		if i == num_wps-1:
			rospy.loginfo("Spin Maneuver")
			spin = True
			while spin:
				time.sleep(1)
			ready_pub.publish(True)

def set_curr(data):
	global curr_x, curr_y, curr_orient
	curr_x,curr_y = data.pose.position.x, data.pose.position.y
	curr_orient = data.pose.orientation


def wp_pub_sub():
	global curr_x,curr_y,curr_orient,next_wp,ready_pub,spin
	next_wp.pose.position.z = 0.5
	rospy.init_node('UAV_setpoint',log_level=rospy.DEBUG,anonymous=True)
	rospy.Subscriber('next_wps',Waypoints,setpoints)
	rospy.Subscriber('slam_out_pose',PoseStamped,set_curr)
	rate = rospy.Rate(15)
	wp_pub = rospy.Publisher('/mavros/setpoint_position/local', PoseStamped, queue_size=10)
	ready_pub = rospy.Publisher('ready_for_wps', Bool, queue_size=10)
	spin_flag = 0
	spin = False
	while not rospy.is_shutdown():
		pos = PoseStamped()
		pos.header.stamp = rospy.Time.now()
		pos.pose.position.x = next_wp.pose.position.x
		pos.pose.position.y = next_wp.pose.position.y
		pos.pose.position.z = next_wp.pose.position.z
		if spin:
			if spin_flag:
				rospy.loginfo("Yaw Left")
				yaw = pi
			else:
				rospy.loginfo("Yaw Right")
				yaw = 0
			quat = qfe(0,0,yaw)
			pos.pose.orientation.x = quat[0]
			pos.pose.orientation.y = quat[1]
			pos.pose.orientation.z = quat[2]
			pos.pose.orientation.w = quat[3]
			wp_pub.publish(pos)
			curr_yaw = efq(curr_orient.x,curr_orient.y,curr_orient.z,curr_orient.w)[-1]
			if abs(curr_yaw - yaw) < epsilon:
				spin_flag ^= 1
				if yaw == 0:
					spin = False
			rate.sleep()
			continue
		quat = qfe(0,0,pi/2)
		pos.pose.orientation.x = quat[0]
		pos.pose.orientation.y = quat[1]
		pos.pose.orientation.z = quat[2]
		pos.pose.orientation.w = quat[3]
		wp_pub.publish(pos)
		rate.sleep()


if __name__ == '__main__':
	global curr_x,curr_y,next_wp
	next_wp = PoseStamped()
	try:
		wp_pub_sub()
	except rospy.ROSInterruptException:
		pass
