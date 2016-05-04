#!/usr/bin/env python
import rospy
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Range

global Time, UAVPose
UAVPose = PoseStamped()

def set_pose(pose):
	global UAVPose
	UAVPose.pose.position.x = pose.pose.position.x
	UAVPose.pose.position.y = pose.pose.position.y
	UAVPose.pose.orientation.z = pose.pose.orientation.z
	UAVPose.pose.orientation.w = pose.pose.orientation.w

def set_alt(range):
	global UAVPose
	UAVPose.pose.position.z = range.range
	

def nodes():
	rospy.init_node('UAV_pose')
	rospy.Subscriber('/Test_Quad_1/pose',PoseStamped,set_pose)
	rospy.Subscriber('/mavros/px4flow/ground_distance',Range,set_alt)
	pub = rospy.Publisher('/mavros/vision_pose/pose',PoseStamped,queue_size=10)
	rate = rospy.Rate(10)
	while not rospy.is_shutdown():
		time = rospy.Time.now()
		UAVPose.header.stamp = time
		pub.publish(UAVPose)
		rate.sleep()

if __name__ == '__main__':
	try:
		nodes()
	except rospy.ROSInterruptException:
		pass
