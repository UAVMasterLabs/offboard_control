#!/usr/bin/env python
import rospy
from geometry_msgs.msg import TwistStamped

def vel_set():
    pub = rospy.Publisher('/mavros/setpoint_velocity/cmd_vel', TwistStamped, queue_size=10)
    rospy.init_node('vel_set_node', anonymous=True)
    rate = rospy.Rate(20) # 10hz
    frame_id = 1
    while not rospy.is_shutdown():
        vel = TwistStamped()
        vel.header.stamp = rospy.Time.now()
        vel.twist.linear.x=0.5
        vel.twist.linear.y=0
        vel.twist.linear.z=0
        pub.publish(vel)
        frame_id += 1
        rate.sleep()

if __name__ == '__main__':
    try:
        vel_set()
    except rospy.ROSInterruptException:
        pass
