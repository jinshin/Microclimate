#!/bin/bash

loglines=7

GREEN=90f090
RED=f09090
BLUE=9090f0
YELLOW=f0f090

#text size color
print_text () {
echo \<font size = $2 color=$3\>$1  \</font\>
}

print_text_line () {
echo \<font size = $2 color=$3\>$1\</font\>\<br\>
}

counter=0
ac=0
for i in `tail -$loglines /var/log/co2`
        do
	case $((counter%7)) in
	0)
	adate[ac*2]=$i
	;;
	1)
	adate[ac*2+1]=$i
	;;
	2)
	aco2[ac]=$i
	;;
	3)
	atemp[ac]=$i
	;;
	4)
	arh[ac]=$i
	;;
        6)
        ((ac++))
	;;
	esac
((counter++))
done

counter=0
bc=0
for i in `tail -$loglines /var/log/heat`
        do
        case $((counter%6)) in
        0)
        bdate[bc*2]=$i
        ;;
        1)
        bdate[bc*2+1]=$i
        ;;
        2)
        btemp[bc]=$i
        ;;
        3)
        bpress[bc]=$i
        ;;
        4)
        brh[bc]=$i
        ;;
        5)
        bht[bc]=$i
        ((bc++))
        ;;
        esac
        ((counter++))
done

echo "<html>"
echo "<meta http-equiv=refresh content=60>"
echo "<body bgcolor=black>"

echo '<style> body { font: normal 10px Verdana, Arial, sans-serif; } </style>'

print_text_line "${adate[0]} ${adate[1]} -> ${adate[($loglines-1)*2]} ${adate[($loglines-1)*2+1]}" 3 gray

echo "<br>"

print_text_line "CO2 Level, PPM" 5 white

fsize=1
for i in ${aco2[*]}
do
	if [ $i -lt "1000" ]
	then
	print_text $i $fsize $GREEN
	elif [ $i -lt "1500" ]
	then
	print_text $i $fsize $YELLOW
        else
        print_text $i $fsize $RED
	fi
((fsize++))
done

echo "<br>"
echo "<br>"

#print_text_line "Relative humidity, Percent" 5 white
#fsize=1
#for i in ${arh[*]}
#do
#        if [ $i -lt "50" ]
#        then
#        print_text $i $fsize green
#        elif [ $i -lt "75" ]
#        then
#        print_text $i $fsize yellow
#        else
#        print_text $i $fsize red
#        fi
#((fsize++))
#done
#echo "<br>"

print_text_line "Temperature, Celsius" 5 white
fsize=1
for i in ${btemp[*]}
do
        if [ `printf "%.*f" 0 $i` -lt "17" ]
        then
        print_text $i $fsize $BLUE
        elif [  `printf "%.*f" 0 $i` -lt "26" ]
        then
        print_text $i $fsize $GREEN
        else
        print_text $i $fsize $RED
        fi
((fsize++))
done

echo "<br>"
echo "<br>"

print_text_line "Heater State" 5 white
fsize=1
for i in ${bht[*]}
do
        if [ $i == "0" ]
        then
        print_text Off $fsize $BLUE
        elif [ $i == "2" ]
        then
        print_text NN $fsize $GREEN
        else
        print_text On $fsize $RED
        fi
((fsize++))
done

echo "<br>"
echo "<br>"
echo "<br>"

echo "<table cellspacing=10 cellpadding=5><tr>"
echo '<td><form action="heaton.sh" method="POST"><INPUT TYPE="submit" VALUE="Run Heater" 
style="height:100px; width:300px;    font-size:30px; background-color:#F0A0A0; border-radius:25px; border:2px solid "white";" ></form></td>'
echo '<td><form action="heatoff.sh" method="POST"><INPUT TYPE="submit" VALUE="Stop Heater"
style="height:100px; width:300px;  font-size:30px; background-color:#A0F0F0; border-radius:25px; border:2px solid "white";" ></form></td>'
echo "</tr><tr>"
echo '<td><form action="autodis.sh" method="POST"><INPUT TYPE="submit" VALUE="Disable Autocontrol"
style="height:100px; width:300px;    font-size:30px; background-color:#F0F0A0; border-radius:25px; border:2px solid "white";" ></form></td>'
echo '<td><form action="autoen.sh" method="POST"><INPUT TYPE="submit" VALUE="Enable Autocontrol"
style="height:100px; width:300px;    font-size:30px; background-color:#A0A0F0; border-radius:25px; border:2px solid "white";" ></form></td>'
echo "</tr><tr>"
echo '<td><form action="ventoff.sh" method="POST"><INPUT TYPE="submit" VALUE="Stop Ventilation"
style="height:100px; width:300px;    font-size:30px; background-color:#F0A0A0; border-radius:25px; border:2px solid "white";" ></form></td>'
echo '<td><form action="venton.sh" method="POST"><INPUT TYPE="submit" VALUE="Start Ventilation"
style="height:100px; width:300px;    font-size:30px; background-color:#A0F0A0; border-radius:25px; border:2px solid "white";" ></form></td>'
echo "</tr></table>"

echo "<br>"

echo "<img src="t.png"><br>"
echo "<img src="p.png"><br>"
echo "<img src="h.png"><br>"
echo "<img src="co2.png"><br>"

print_text_line "Generated: `date`" 3 gray

echo "</body>"
echo "</html>"
