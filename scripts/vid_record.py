#!/usr/bin/env python
import rospy
from mavros_msgs.msg import State
from std_msgs.msg import String

import picamera
from time import ctime

from threading import Thread

def set_record(data):
	global Record
	if not Record and data.armed:
		Record = True
	elif not data.armed:
		Record = False
	else:
		pass

def arm_watch():
	global Record
	Record = False
	rospy.init_node('UAV_cam')
	rospy.Subscriber('/mavros/state',State,set_record)
	rospy.spin()

def record():
	global Record
	geotiff_pub = rospy.Publisher('syscommand',String,queue_size=10)
	with picamera.PiCamera() as cam:
		cam.resolution = (640,480)
		cam.rotation = 180
		while not rospy.is_shutdown():
			now = ctime().replace(' ','_').replace(':','-')
			if Record:
				cam.start_recording('/media/tunnel_usb/tunnel_test'+now+'.h264')
				rospy.loginfo('Vid recording started')
				while Record:
					cam.wait_recording(1)
				cam.stop_recording()
				geotiff_pub.publish('savegeotiff')
				rospy.loginfo('Vid recording stopped')

if __name__ == '__main__':
	try:
		cam_thread = Thread(target = record)
		cam_thread.daemon = True
		cam_thread.start()
		arm_watch()
	except rospy.ROSInterruptException:
		pass
			
