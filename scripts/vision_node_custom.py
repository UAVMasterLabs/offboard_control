#!/usr/bin/env python
import rospy
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Pose2D

global Time

def set_pose(pose):
	global Time
	if rospy.Time.now() - Time < rospy.Duration(0.05):
		return
	#print 'publishing mocap'
	Pose = pose.pose
	pub = rospy.Publisher('/mavros/mocap/pose',PoseStamped,queue_size = 10)
	newPose = PoseStamped()
	Time = rospy.Time.now()
	newPose.header.stamp = Time
	newPose.pose = Pose
	pub.publish(newPose)

	

def mocap_sub():
	global Time
	rospy.init_node('mocap_pose_getter')
	Time = rospy.Time.now()
	rospy.Subscriber('/Test_Quad_1/pose',PoseStamped,set_pose)
	rospy.spin()

def mocap_pub(pose):
	rate = rospy.Rate(20)
	while not rospy.is_shutdown():
		rate.sleep()

if __name__ == '__main__':
	mocap_sub()
