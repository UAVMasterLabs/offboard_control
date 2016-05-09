#!/usr/bin/env python
from __future__ import division
import rospy
from geometry_msgs.msg import PoseStamped
from tf.transformations import quaternion_from_euler as qfe
from numpy import pi

def pos_set():
    pub = rospy.Publisher('/mavros/setpoint_position/local', PoseStamped, queue_size=10)
    rospy.init_node('UAV_setpoint')
    rate = rospy.Rate(20)
    frame_id = 1
    while not rospy.is_shutdown():
        pos = PoseStamped()
        pos.header.stamp = rospy.Time.now()
        pos.pose.position.x=0
        pos.pose.position.y=0
        pos.pose.position.z=0.5
        quat = qfe(0,0,0)
        pos.pose.orientation.w = quat[3]
        pos.pose.orientation.x = quat[0]
        pos.pose.orientation.y = quat[1]
        pos.pose.orientation.z = quat[2]
        pub.publish(pos)
        frame_id += 1
        rate.sleep()

if __name__ == '__main__':
    try:
        pos_set()
    except rospy.ROSInterruptException:
        pass
