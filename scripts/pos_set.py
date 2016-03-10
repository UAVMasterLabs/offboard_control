#!/usr/bin/env python
import rospy
from geometry_msgs.msg import PoseStamped

def pos_set():
    pub = rospy.Publisher('/mavros/setpoint_position/local', PoseStamped, queue_size=10)
    rospy.init_node('pos_set_node', anonymous=True)
    rate = rospy.Rate(20) # 10hz
    frame_id = 1
    while not rospy.is_shutdown():
        pos = PoseStamped()
        pos.header.frame_id = 'world'
        pos.header.stamp = rospy.Time.now()
        pos.pose.position.x=0
        pos.pose.position.y=0
        pos.pose.position.z=1
        pub.publish(pos)
        frame_id += 1
        rate.sleep()

if __name__ == '__main__':
    try:
        pos_set()
    except rospy.ROSInterruptException:
        pass
