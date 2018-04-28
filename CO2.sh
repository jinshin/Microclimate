#!/bin/bash
ps aux | grep "home/pi/co2.py" | grep -v "grep"
if [ "$?" == "1" ]
then
        /usr/bin/python3 /home/pi/co2.py &
fi
