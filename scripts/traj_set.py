#!/usr/bin/env python
from __future__ import division
import rospy, time
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Bool
from offboard.msg import Waypoints
from mavros_msgs.msg import State
from tf.transformations import quaternion_from_euler as qfe
from tf.transformations import euler_from_quaternion as efq
from numpy import pi,sqrt

def setpoints(data):
	global next_wp, ready_pub,spin,size,all_waypoints, rtl
	rospy.loginfo('Recieved waypoints')
	ready_pub.publish(False) #let us execute the path before sending any more info to sentel
	x_dist,y_dist = [],[]
	x_ways = data.x
	y_ways = data.y
	num_wps = len(x_ways)
	for i in range(num_wps):
		x_dist.append((y_ways[i] - size/2)*0.05) #subscpribe to grid waypoints
		y_dist.append(-(x_ways[i] - size/2)*0.05) # and translate to relative distance from current coordinate location
						       # This is probably where x -> y, -y -> x should occur? Correct. Not done properly yet
						       # Confirm this using rostpoic echo /mavros/setpoint_position/local? 
	# To confirm, keep doing your flight tests and see what setpoint_position/local vs /slam_out_pose look like
	# and then make these waypoints look similar by some rotation to get good behavior
	# You will know you have reched the waypoint when your setpoint changes to ask for a spin maneuver
	# Once the spin is complete, map from map_viewer will update and you will get new translational waypoints
	x_wps = [curr_x+x for x in x_dist]
	y_wps = [curr_y+y for y in y_dist]
	all_waypoints.x = all_waypoints.x + x_wps
	all_waypoints.y = all_waypoints.y + y_wps
	epsilon = 0.10 #m radius for achieved waypoint
	for i in range(num_wps):
		dx = abs(x_wps[i] - curr_x)
		dy = abs(y_wps[i] - curr_y)
		radius = sqrt(dx**2 + dy**2) #Find norm
		while radius > epsilon:
			dx = abs(x_wps[i] - curr_x)
			dy = abs(y_wps[i] - curr_y)
			radius = sqrt(dx**2 + dy**2) #Find norm
			rospy.loginfo("c_x: %s, d_x: %s -- c_y: %s, d_y: %s -- rad: %s",str(curr_x)[:4],str(x_wps[i])[:4],str(curr_y)[:4],str(y_wps[i])[:4],str(radius)[:4])
			next_wp.pose.position.x = x_wps[i]
			next_wp.pose.position.y = y_wps[i]
		if i == num_wps-1:
			if rtl:
				next_wp.pose.position.z = 0
			rospy.loginfo("Spin Maneuver")
			spin = True
			while spin:
				time.sleep(1)
#			first_pub.publish(True)

def set_curr(data):
	global curr_x, curr_y, curr_orient
	curr_x,curr_y = data.pose.position.x, data.pose.position.y
	curr_orient = data.pose.orientation

def set_curr_z(data):
	global curr_z
	curr_z = data.pose.position.z

def get_curr_mode(data):
	global mode
	mode = data.mode

def get_voltage(data):
	global rtl
	if data.voltage < 11.8:
		rtl = True

def get_rtl(data):
	global rtl
	rtl = data.data

def wp_pub_sub():
	global curr_x,curr_y,curr_orient,next_wp,ready_pub,spin,mode,size,rtl,all_waypoints,first_pub
	next_wp.pose.position.z = 0.4
	all_waypoints = Waypoints()
	rospy.init_node('UAV_setpoint',anonymous=True)
	rospy.Subscriber('next_wps',Waypoints,setpoints)
	rospy.Subscriber('/mavros/state',State,get_curr_mode)
	rospy.Subscriber('slam_out_pose',PoseStamped,set_curr)
	rospy.Subscriber('/mavros/local_position/pose',PoseStamped,set_curr_z)
	rospy.Subscriber('return_to_launch',Bool,get_rtl)
	rate = rospy.Rate(15)
	wp_pub = rospy.Publisher('/mavros/setpoint_position/local', PoseStamped, queue_size=10)
	ready_pub = rospy.Publisher('ready_for_wps', Bool, queue_size=10)
	rtl_pub = rospy.Publisher('return_to_launch', Bool, queue_size=10)
	rtl_path_pub = rospy.Publisher('next_wps', Waypoints, queue_size=10)
	first_pub = rospy.Publisher('first_wps', Bool, queue_size=10)
	spin_flag = 0
	spin = False
	spins = 0
	offboard_counter = 0
	rtl_flag = 0
	size = 128
	while not rospy.is_shutdown():
		if 'mode' in globals() and mode in "OFFBOARD":
			offboard_counter += 1
			#rospy.loginfo(str(offboard_counter))
			if 0 > offboard_counter <= 5:
				rospy.loginfo("Just entered OFFBOARD mode")
		pos = PoseStamped()
		pos.header.stamp = rospy.Time.now()
		pos.pose.position.x = next_wp.pose.position.x #these lines could also be changed instead of above
		pos.pose.position.y = next_wp.pose.position.y
		pos.pose.position.z = next_wp.pose.position.z #this line can be changed to reflect desired z setpoints
		#if 'curr_z' in globals():
		#	rospy.loginfo('spins:%s,curr_z:%s,offboard_counter:%s',str(spins),str(curr_z),str(offboard_counter))
		if spins == 0 and 'curr_z' in globals() and curr_z > 0.15 and offboard_counter >= 50:
			rospy.loginfo("executing first spin maneuver")
			spin = True
			first_pub.publish(True)
		if spins%5:
			spin = False
		if spin:
			# Yaw is in /slam_out_pose frame.
			if spin_flag == 1:
				rospy.loginfo("Yaw Left")
				yaw = pi/8
			elif spin_flag == 0:
				rospy.loginfo("Yaw Right")
				yaw = -pi/8
			else:
				rospy.loginfo("Yaw Back")
				yaw = 0
			quat = qfe(0,0,yaw+pi/2)#euler angles -- RPY roll pitch yaw --> Q xyzw 
						#add pi/2 to send to setpoint_position/local
			pos.pose.orientation.x = quat[0]
			pos.pose.orientation.y = quat[1]
			pos.pose.orientation.z = quat[2]
			pos.pose.orientation.w = quat[3]
			wp_pub.publish(pos)
			while not 'curr_orient' in globals():
				time.sleep(0.01)
			curr_yaw = efq([curr_orient.x,curr_orient.y,curr_orient.z,curr_orient.w])[-1]
			#rospy.loginfo('curr_yaw: %s, des_yaw: %s',str(curr_yaw),str(yaw))
			epsilon = 0.1
			if abs(curr_yaw - yaw) < epsilon:
				spin_flag += 1
				if yaw == 0:
					spin = False
					spin_flag = 0
					ready_pub.publish(True) #ready for more waypoints. send nav_map to sentel
					spins += 1
			rate.sleep()
			continue # this tells us to skip everything else in the loop and start from the top, (skip next 7 lines)
		if 'rtl' in globals() and rtl and not rtl_flag:
			rtl_flag = 1
			rtl_pub.publish(True)
			rtl_wps = Waypoints()
			rtl_wps.x = list(reversed(all_waypoints.x))
			rtl_wps.y = list(reversed(all_waypoints.y))
			rtl_path_pub.publish(rtl_wps)
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
