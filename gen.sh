#!/bin/bash

loglines=7

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

echo "<html>"
echo "<body bgcolor=black>"
print_text_line "${adate[0]} ${adate[1]} -> ${adate[($loglines-1)*2]} ${adate[($loglines-1)*2+1]}" 3 gray

print_text_line "CO2 Level, PPM" 5 white

fsize=1
for i in ${aco2[*]}
do
        if [ $i -lt "1000" ]
        then
        print_text $i $fsize green
        elif [ $i -lt "1500" ]
        then
        print_text $i $fsize yellow
        else
        print_text $i $fsize red
        fi
((fsize++))
done

echo "<br>"

print_text_line "Relative humidity, Percent" 5 white
fsize=1
for i in ${arh[*]}
do
        if [ $i -lt "50" ]
        then
        print_text $i $fsize green
        elif [ $i -lt "75" ]
        then
        print_text $i $fsize yellow
        else
        print_text $i $fsize red
        fi
((fsize++))
done

echo "<br>"

print_text_line "Temperature, Celsius" 5 white
fsize=1
for i in ${atemp[*]}
do
        if [ $i -lt "17" ]
        then
        print_text $i $fsize blue
        elif [ $i -lt "26" ]
        then
        print_text $i $fsize green
        else
        print_text $i $fsize red
        fi
((fsize++))
done

echo "<br>"
print_text_line "Generated: `date`" 3 gray

echo "</body>"
echo "</html>"
