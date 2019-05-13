#!/bin/sh
# /etc/init.d/discovery.sh
### BEGIN INIT INFO
# Provides:	  discovery.sh
# Required-Start:    $network
# Required-Stop:     $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: discovery for webcam
# Description:       Streams /dev/video0 to http://IP/?action=stream
### END INIT INFO

f_message(){
	echo "[+] $1"
}
 
# Carry out specific functions when asked to by the system
case "$1" in
	start)
		/root/evdevice/services/udps.py
		f_message "Starting udps"
		#start service as per master or slave	
		sleep 2
		f_message "discovery service started"
		;;
	stop)
		pid=`ps -ef | grep "udps.py" | grep -v "grep" | awk '{print $2}' | head -n 1`
		kill -9 $pid
		f_message "discovery stopped"
		;;
	restart)
		f_message "Restarting discovery"
		pid=`ps -ef | grep "udps.py" | grep -v "grep" | awk '{print $2}' | head -n 1`
		kill -9 $pid
		/root/evdevice/services/udps.py
		f_message "Starting udps"
		#start service as per master or slave	
		sleep 2
		f_message "discovery service started"
		;;
	status)
		pid=`ps -ef | grep "udps.py" | grep -v "grep" | awk '{print $2}' | head -n 1`

		if [ -n "$pid" ];
		then
			f_message "discovery is running with pid ${pid}"
			f_message "discovery was started with the following command line"
			cat /proc/${pid}/cmdline ; echo ""
		else
			f_message "Could not find discovery running"
		fi
		;;
	*)
		f_message "Usage: $0 {start|stop|status|restart}"
		exit 1
		;;
esac
exit 0


