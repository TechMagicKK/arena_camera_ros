#!/bin/bash -e

[ $# -eq 0 ] && echo "ROS VERSION is not specified" && exit 1

source /opt/ros/$1/setup.bash

CATKIN_WS=$HOME/catkin_ws

if [ ! -e $CATKIN_WS ]; then
    mkdir -p $CATKIN_WS
    cd $CATKIN_WS
    catkin init
else
    cd $CATKIN_WS
fi

cat <<EOL | sed -r '/^\s*$/d' | xargs -n1 -I@ ln -s /app/catkin_ws/@ ./@
inc
src
EOL

cd /app/ArenaSDK_Linux_x64
sh Arena_SDK_Linux_x64.conf -r

cd $CATKIN_WS
sh /app/ros_and_workspace_setup.sh

source $HOME/.bashrc
source /opt/ros/$1/setup.bash
catkin build -j$(nproc)
