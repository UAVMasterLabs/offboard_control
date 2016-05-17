#!/usr/bin/env python
import rospy, serial, time
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import RCIn

def rebooter(data):
	global channel6
	if len(data.channels) < 5:
		return
	if data.channels[5] > 1500:
		channel6 = True

def sub():
	global channel6
	rospy.init_node('reboot')
	rospy.Subscriber('/mavros/rc/in',RCIn,rebooter)
	while 'channel6' not in globals() or not channel6:
		time.sleep(1)

if __name__ == '__main__':
	sub()
	pix = serial.Serial('/dev/ttyUSB0',57600)
	pix.flush()
	pix.write(b'\r\n')
	pix.write(b'reboot\r\n')
	time.sleep(3)
        pix.flush()
	pix.write(b'\r\n')
	pix.write(b'tone_alarm MFT225O3L8GL8GL8GL2E-P8L8FL8FL8FMLL2DL2DMNP8\r\n')
	pix.close()
