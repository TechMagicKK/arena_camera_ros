#!/bin/bash

source /opt/ros/melodic/setup.bash
source /root/catkin_ws/devel/setup.bash

roslaunch --wait arena_camera arena_camera_node.launch
