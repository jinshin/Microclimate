import serial, sched, time, socket

VentoIP = '10.10.10.10'
VentoPort = 4000

#Min
CO2_Level = 400
Vent_Speed = 22
CO2_Prev = CO2_Level
Speed_Prev = Vent_Speed
Temp = 0
Power_On = 0

def get_co2():
        global Temp
        ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.5)
        try:
                result=ser.write(bytes([0xff,0x01,0x86,0x00,0x00,0x00,0x00,0x00,0x79]))
        except:
                return 0
        time.sleep(0.1)
        try:
                s=ser.read(9)
        except:
                return 0
        chk = (s[1]+s[2]+s[3]+s[4]+s[5]+s[6]+s[7])%256
        chk = (0xff - chk) + 1
        if chk != s[8]:
                #CRC invalid, return 0
                return 0
        if s[0] == 0xff and s[1] == 0x86:
                Temp = s[4]-40
                return s[2]*256 + s[3]

def set_speed(speed):
        global VentoIP
        global VentoPort
        Device = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        Device.settimeout(1)
        sendstr = bytes('mobile','cp1251')
        sendstr = sendstr + bytes([0x05]) + (Vent_Speed.to_bytes(1, byteorder='big')) + bytes([0xD, 0xA])
        #print (sendstr)
        Device.sendto(sendstr, (VentoIP, VentoPort))
        Device.close()

def switch_power():
        global VentoIP
        global VentoPort
        Device = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        Device.settimeout(1)
        sendstr = bytes('mobile','cp1251')
        sendstr = sendstr + bytes([0x03, 0x01, 0xD, 0xA])
        Device.sendto(sendstr, (VentoIP, VentoPort))
        Device.close()

def get_speed():
        global VentoIP
        global VentoPort
        global Power_On
        Device = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        Device.settimeout(1)
        sendstr = bytes('mobile','cp1251')
        sendstr = sendstr + bytes([0x01, 0xD, 0xA])
        try:
                Device.sendto(sendstr, (VentoIP, VentoPort))
        except:
                return 0
        try:
                Received, addr = Device.recvfrom(256)
        except:
                return 0
        Device.close()
        if Received[0:6] == b'master':
                X = 6
                while X < len (Received):
                        SW = Received[X]
                        if SW == 3:
                                X+=1
                                Power_On = Received[X]
                                #print('Power: ',Received[X])
                        if SW == 4:
                                X+=1
                                #print('Preset speed: ',Received[X])
                                if Received[X] != 4:
                                        return (22+(Received[X]-1)*((255-22)/2))
                        if SW == 5:
                                X+=1
                                #print('Manual speed: ',Received[X])
                                return (Received[X])
                        X+=1
        return 0

CO2_Prev = 0
Speed_Prev = 0

def change_speed(speed_val):
     global Speed_Prev
     global Vent_Speed
     Speed_Prev = Vent_Speed
     Vent_Speed = Vent_Speed + speed_val
     if Vent_Speed > 255:
        Vent_Speed = 255
     elif Vent_Speed < 22:
        Vent_Speed = 22
     if Vent_Speed != Speed_Prev:
         set_speed(Vent_Speed)

def time_func():
    global CO2_Level
    global Vent_Speed
    global CO2_Prev
    global Speed_Prev
    s.enter(60, 1, time_func, ())
    CO2_Level = get_co2()
    if CO2_Level == 0:
        return
    Vent_Speed = get_speed()
    if Vent_Speed == 0:
        return
    #print (CO2_Level, Temp, Vent_Speed)
    if CO2_Level > 1000 and CO2_Prev < CO2_Level:
        change_speed(12)
    elif CO2_Level < 750 and CO2_Prev >= CO2_Level:
        change_speed(-12)
    if CO2_Level <= 650 and Vent_Speed == 22 and Power_On == 1:
        switch_power()
    if CO2_Level > 800 and Power_On == 0:
        switch_power()
    CO2_Prev = CO2_Level
    log_file = open("/var/log/co2.log", "a")
    log_file.write(time.strftime("%Y-%m-%d %H:%M")+" "+str(CO2_Level)+" "+str(Temp)+" "+str(Vent_Speed)+" "+str (Power_On)+"\r\n")
    log_file.close()

print("Starting.")

CO2_Prev = get_co2()
Speed_Prev = get_speed()

s = sched.scheduler(time.time, time.sleep)
s.enter(1, 1, time_func, ())
s.run()

while True:
        time.sleep(1)
