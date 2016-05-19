#!/usr/bin/env python
import rospy
from mavros_msgs.msg import State
from std_msgs.msg import String

import socket, io, subprocess
from time import ctime,time,sleep
import os, signal
from shutil import copy

from threading import Thread

def set_record(data):
	global Record
	if not Record and data.armed:
		rospy.loginfo('Record:%s',str(Record))
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
	vid_cmd = 'raspivid -t 0 -h 720 -w 1080 -fps 25 -hf -vf -b 2000000 -o - '
	record_cmd = ' tee -a '
	gst_cmd = ' gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=192.168.0.189 port=5000'
	Record = False
	while not rospy.is_shutdown():
		start = time()
		now = ctime().replace(' ','_').replace(':','-')
		vid_file = '/media/tunnel_usb/tunnel_test'+now+'.h264 '
		cmd = vid_cmd + '|' + record_cmd + vid_file + '|' + gst_cmd
		if Record:
			vid_ps = subprocess.Popen(vid_cmd,stdout=subprocess.PIPE,shell=True,preexec_fn=os.setsid)
			rospy.loginfo('Vid pid:%s',str(vid_ps.pid))
			rospy.loginfo('Vid recording started')
			while Record:
				if not int(time() - start)%30:
					geotiff_pub.publish('savegeotiff')
			os.killpg(os.getpgid(vid_ps.pid),signal.SIGTERM)
			geotiff_pub.publish('savegeotiff')
			rospy.loginfo('Vid recording stopped')
			sleep(3)
			new_tiffs = [f for f in os.listdir(filepath) if ':' in f]
			rospy.loginfo('I have the new files')
			for f in new_tiffs:
				copy(filepath+f,'/media/tunnel_usb/maps/'+f.replace(':','-'))
			rospy.loginfo('Done copying the new maps')

if __name__ == '__main__':
	try:
		filepath = '/home/pi/tunnel_ws/src/hector_slam/hector_geotiff/maps/'
		cam_thread = Thread(target = record)
		cam_thread.daemon = True
		cam_thread.start()
		arm_watch()
	except rospy.ROSInterruptException:
		pass
			
