Workflow:
launch offboard_slam.launch with:
$roslaunch offboard offboard_slam.launch

This will launch all of the necessary scripts.
To view output from any particular script (i.e - read out yaw commands from traj_set.py),
comment out the corresponding line from offboard_slam.launch (<node=.../> becomes <!--node=.../-->).
Once it is commented out, it will no longer be launched automatically and you can
run the script in a separate terminal windows with e.g.:
$rosrun offboard traj_set.py
This will print any ```rospy.loginfo("<output>")``` to the terminal screen.

To view the map:
```$rosrun offboard map_viewer.py```

To view your setpoint (ROS frame - ENU):
```$rostopic echo /mavros/setpoint_position/local```

To view your current pose (slam frame - FLU):
```$rostopic echo /slam_out_pose```

Other useful topics to get info from:
/ready_for_wps -- self-explanatory
/next_wps -- in slam frame grid locations


If you make any edits and test them to success, push out to the repo
```$git add -A
$git commit
# this will send you to nano. Write a quick descr of what you did
#CTRL-x, y, ENTER to save and exit
$git push
#this will prompt for UN and PW```
