#!/bin/bash -x

WORKDIR=$HOME/Work

function up {
    echo "Startup arena camera driver"
    docker compose -f $WORKDIR/arena_camera_ros/docker-compose.yaml up -d driver
    sleep 1

    echo "Startup calibration services"
    docker compose -f $WORKDIR/mnrobot_core/docker-compose.helios_calibrate_test.yaml up -d
}

function down {
    echo "Terminate arena camera driver"
    docker compose -f $WORKDIR/arena_camera_ros/docker-compose.yaml down
    sleep 1

    echo "Terminate calibration services"
    docker compose -f $WORKDIR/mnrobot_core/docker-compose.helios_calibrate_test.yaml down
}

subcomand=$1

case $subcomand in
    up)
        up
        ;;
    down)
        down
        ;;
    *)
        echo "Invalid subcommand"
        ;;
esac
