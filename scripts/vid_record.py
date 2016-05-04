import rospy
from mavros_msgs.msg import State

import picamera
from time import ctime

def set_record(data):
	if not Record and data.armed:
		Record = True
	else if not data.armed:
		Record = False
	else
		pass

def arm_watch():
	global Record
	Record = False
	record()
	rospy.init_node('UAV_cam')
	rospy.Subscriber('/mavros/state',State,set_record)
	rospy.spin()

def record():
	global Record
	with picamera.PiCamera() as cam:
		cam.resolution = (640,480)
		while not rospy.is_shutdown():
			now = ctime()
			if Record:
				cam.start_recording('/media/tunnel_usb/tunnel_test'+now+'.h264')
				while Record:
					cam.wait_recording(1)
				cam.stop_recording()

if __name__ == '__main__':
	try:
		arm_watch()
	except rospy.ROSInterruptException:
		pass
			
