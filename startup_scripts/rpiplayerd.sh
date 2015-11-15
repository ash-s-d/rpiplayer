#! /bin/sh
# /etc/init.d/rpiplayerd
#

PYTHON=/usr/bin/python

APP_PATH=/opt/rpiplayer/
SCRIPT=rpiplayerd.py

start(){
	cd $APP_PATH
	$PYTHON $APP_PATH$SCRIPT --start
}

stop(){
	cd $APP_PATH	
	$PYTHON $APP_PATH$SCRIPT --stop
}

restart(){
	cd $APP_PATH	
	$PYTHON $APP_PATH$SCRIPT --restart
}

case "$1" in
	start)
		start
		;;
	stop)
		stop
		;;
	restart)
		restart
		;;
	*)
		echo "USAGE: /etc/init.d/rpiplayerd {start|stop|restart}"
		exit 1 
		;;
esac

exit 0