#!/bin/bash
ps aux | grep "home/n0p/bme280.py" | grep -v "grep"
if [ "$?" == "1" ]
then
	/usr/bin/python3 /home/n0p/bme280.py &
fi
