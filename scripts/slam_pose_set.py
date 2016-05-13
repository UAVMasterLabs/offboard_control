#!/usr/bin/env python
import rospy
from geometry_msgs.msg import PoseStamped,PoseWithCovarianceStamped
from sensor_msgs.msg import Range

def set_pose(pose):
	global UAVPose
#	UAVPose.pose.position.x = pose.pose.position.x
#	UAVPose.pose.position.y = pose.pose.position.y
#	UAVPose.pose.orientation.z = pose.pose.orientation.z
#	UAVPose.pose.orientation.w = pose.pose.orientation.w
# The frame needs to taken into account here. Need to see what frame hector_slam
# is outputting and which frame we need to rotate to.
	UAVPose.pose.pose.position.x = pose.pose.pose.position.x
	UAVPose.pose.pose.position.y = pose.pose.pose.position.y
	UAVPose.pose.pose.orientation.z = pose.pose.pose.orientation.z
	UAVPose.pose.pose.orientation.w = pose.pose.pose.orientation.w
	UAVPose.pose.covariance = pose.pose.covariance

def set_alt(range):
	global UAVPose
#	UAVPose.pose.position.z = range.range
	UAVPose.pose.pose.position.z = range.range
	
def nodes():
	rospy.init_node('UAV_pose')
#	rospy.Subscriber('/Test_Quad_1/pose',PoseStamped,set_pose)
#	rospy.Subscriber('/slam_out_pose',PoseStamped,set_pose)
	rospy.Subscriber('/poseupdate',PoseWithCovarianceStamped,set_pose)
#	rospy.Subscriber('/mavros/px4flow/ground_distance',Range,set_alt)
	rospy.Subscriber('/mavros/distance_sensor/hrlv_ez4_pub',Range,set_alt)
#	pub = rospy.Publisher('/mavros/mocap/pose',PoseStamped,queue_size=10)
#	pub = rospy.Publisher('/mavros/vision_pose/pose',PoseStamped,queue_size=10)
	pub = rospy.Publisher('/mavros/vision_pose/pose_cov',PoseWithCovarianceStamped,queue_size=10)
	rate = rospy.Rate(15)
	while not rospy.is_shutdown():
		time = rospy.Time.now()
		UAVPose.header.stamp = time
		pub.publish(UAVPose)
		rate.sleep()

if __name__ == '__main__':
	global UAVPose
#	UAVPose = PoseStamped()
	UAVPose = PoseWithCovarianceStamped()

	try:
		nodes()
	except rospy.ROSInterruptException:
		pass
