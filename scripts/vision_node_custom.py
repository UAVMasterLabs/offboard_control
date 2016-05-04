#!/usr/bin/env python
import rospy
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Pose2D

global Time, UAVPose
UAVPose = PoseStamped()

def set_pose(pose):
	global Time, UAVPose
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

	

def subscribers():
	global Time
	rospy.init_node('UAV_pose')
#	Time = rospy.Time.now()
	rospy.Subscriber('/Test_Quad_1/pose',PoseStamped,set_pose)
	rospy.Subscriber('/Test_Quad_1/pose',PoseStamped,set_pose)
	rospy.spin()

def mocap_pub(pose):
	rate = rospy.Rate(20)
	while not rospy.is_shutdown():
		rate.sleep()

if __name__ == '__main__':
	mocap_sub()
