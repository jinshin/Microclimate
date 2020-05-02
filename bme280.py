import os, smbus, sched, time, datetime
import OPi.GPIO as GPIO

def sbyte (number):
  if number > 127: number -= 256
  return number

PowerPIN=19
OnPIN=21
OffPIN=23

logfile = "/var/log/heat"
dbglog  = "/var/log/bme"
onflag = "/tmp/HEATON"
offflag = "/tmp/HEATOFF"
noauto = "/tmp/AUTOOFF"

Night_Start = datetime.time(23,0,0)
Day_Start = datetime.time(8,0,0)

#Don't control heater on summer
#MMDD
Summer_Start = 501
Winter_Start = 901

Min_Cycle = 10 #minutes heat minimum
Force_Cycle = 30 #Run heater when forced

heat_counter = 0
heat_op = 2       #1 - start, 0 - stop, 2 - not needed

Day_Temp_Max = 18.9
Day_Temp_Min = 18.7
Night_Temp_Max = 17.8
Night_Temp_Min = 17.6
Away_Temp_Max = 15.8
Away_Temp_Min = 15.6
Away_Level = 500 #Anything below considered nobody home

def log_console(data):
  global dbglog
  try:
    log_file = open(dbglog, "a")
    log_file.write(time.strftime("%Y-%m-%d %H:%M")+" "+data+"\n")
    log_file.close()
  except:
    print ("Cannot write to log")

def is_winter():
  global Summer_Start, Winter_Start
  Current_Date = datetime.datetime.now().month*100+datetime.datetime.now().day
  if Winter_Start <= Summer_Start:
    return Winter_Start <= Current_Date <= Summer_Start
  else:
    return Winter_Start <= Current_Date or Current_Date < Summer_Start

def is_night():
  global Night_Start
  global Day_Start
  Current_Time = datetime.datetime.now().time()
  if Night_Start <= Day_Start:
    return Night_Start <= Current_Time <= Day_Start
  else:
    return Night_Start <= Current_Time or Current_Time <= Day_Start

#Global
T1,T2,T3,P1,P2,P3,P4,P5,P6,P7,P8,P9,H1,H2,H3,H4,H5,H6 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
BME280 = 0x76
I2CNUM = 0
i2cdev = 0
CO2LEVEL = 800

def init_bme280():

  global T1,T2,T3,P1,P2,P3,P4,P5,P6,P7,P8,P9,H1,H2,H3,H4,H5,H6
  global BME280
  global I2CNUM
  global i2cdev

  i2cdev = smbus.SMBus(I2CNUM)

  cdataTP = i2cdev.read_i2c_block_data(BME280, 0x88, 26)
  cdataH = i2cdev.read_i2c_block_data(BME280, 0xE1, 7)

  bc = 0
  #it would look much nicer in C
  T1 = cdataTP[bc]+cdataTP[bc+1]*256; bc+=2
  T2 = cdataTP[bc]+sbyte(cdataTP[bc+1])*256; bc+=2
  T3 = cdataTP[bc]+sbyte(cdataTP[bc+1])*256; bc+=2
  P1 = cdataTP[bc]+cdataTP[bc+1]*256; bc+=2
  P2 = cdataTP[bc]+sbyte(cdataTP[bc+1])*256; bc+=2
  P3 = cdataTP[bc]+sbyte(cdataTP[bc+1])*256; bc+=2
  P4 = cdataTP[bc]+sbyte(cdataTP[bc+1])*256; bc+=2
  P5 = cdataTP[bc]+sbyte(cdataTP[bc+1])*256; bc+=2
  P6 = cdataTP[bc]+sbyte(cdataTP[bc+1])*256; bc+=2
  P7 = cdataTP[bc]+sbyte(cdataTP[bc+1])*256; bc+=2
  P8 = cdataTP[bc]+sbyte(cdataTP[bc+1])*256; bc+=2
  P9 = cdataTP[bc]+sbyte(cdataTP[bc+1])*256; bc+=3
  H1 = cdataTP[bc]

  bc = 0
  H2 = cdataH[bc]+sbyte(cdataH[bc+1])*256; bc+=2
  H3 = cdataH[bc]; bc+=1
  E5_L = cdataH[bc+1]&0x0f
  E5_H = (cdataH[bc+1]&0xf0)>>4
  H4 = (sbyte(cdataH[bc])*16) | E5_L
  H5 = (sbyte(cdataH[bc+2])*16) | E5_H
  H6 = sbyte(cdataH[bc+3])


def read_bme280():

  global T1,T2,T3,P1,P2,P3,P4,P5,P6,P7,P8,P9,H1,H2,H3,H4,H5,H6
  global BME280
  global I2CNUM
  global i2cdev

  #Oversampling
  OVS = 2
  #Set humidity oversampling (1,2,3,4,5)
  i2cdev.write_byte_data(BME280, 0xF2, OVS)
  #Set other oversampling and mode and apply humidity (3bits temp oversampling, 3bits pressure oversampling, 2bits mode)
  #forced mode
  i2cdev.write_byte_data(BME280, 0xF4, (OVS<<5)|(OVS<<2)|1 )
  #Set config (3bits standby ms, 3bits IIR, 1 skip, 1 SPI mode)
  #Not for forced mode
  #Calc delay
  DELAY = (1.25+2.3*(1<<OVS) + 2.3*(1<<OVS)+0.58 + 2.3*(1<<OVS)+0.58)/1000
  time.sleep(DELAY)

  #Read uncalibrated data
  udata = i2cdev.read_i2c_block_data(BME280, 0xF7, 8)
  #Set raw values
  pressure = (udata[0]<<12) | (udata[1]<<4) | (udata[2]>>4)
  temperature = (udata[3]<<12) | (udata[4]<<4) | (udata[5]>>4)
  humidity = (udata[6]<<8) | udata[7]

  #Deutsch eyebleed coding
  var1  = ((((temperature//8) - (T1*2))) * (T2)) // 2048
  var2  = (((((temperature//16) - (T1)) * ((temperature//16) - (T1))) // 4096) * (T3)) // 16384
  t_fine = var1 + var2
  T  = (t_fine * 5 + 128) // 256
  ctemperature = T/100

  var1 = t_fine - 128000
  var2 = var1 * var1 * P6
  var2 = var2 + (var1 * P5 * 131072)
  var2 = var2 + (P4*34359738368)
  var1 = ((var1 * var1 * P3)//256) + ((var1 * P2)*4096)
  var1 = (140737488355328+var1)*(P1)//8589934592
  if (var1 != 0):
    p = 1048576 - pressure
    p = (((p*2147483648) - var2)*3125)/var1
    var1 = ((P9) * (p//8192) * (p//8192)) // 33554432
    var2 =((P8) * p) // 524288
    p = ((p + var1 + var2)//256) + ((P7)*16)
    cpressure = round(p/256/100,2)
  else:
    cpressure = 0

  v_x1_u32r = t_fine - 76800;
  v_x1_u32r = (((((humidity * 16384) - (H4 * 1048576) - (H5 * v_x1_u32r)) + 16384) // 32768) * (((((((v_x1_u32r * H6) // 1024) * (((v_x1_u32r * H3) // 2048) + 32768)) // 1024) + 2097152) * H2 + 8192) // 16384))
  v_x1_u32r = (v_x1_u32r - (((((v_x1_u32r // 32768) * (v_x1_u32r // 32768)) // 128) * H1) // 16 ));
  if (v_x1_u32r < 0): v_x1_u32r = 0
  if (v_x1_u32r > 419430400): v_x1_u32r = 419430400
  chumidity = round(v_x1_u32r/4096/1024,2);

  return ctemperature,cpressure,chumidity

last_op = -1
op_count = 0

def heater(on):

  #Signal send rate limiter
  global last_op, op_count
  if (last_op == on):
    op_count+=1
  else:
    last_op=on
    op_count=0
  if ((op_count % 10) != 0):
    log_console("Skip send")
    return

  global GPIO

  #Power sender On
  GPIO.output(OnPIN, 1)
  GPIO.output(OffPIN, 1)
  GPIO.output(PowerPIN, 1)

  #Wake fixup
  time.sleep(3)

  if (on):
    SendPIN=OnPIN
  else:
    SendPIN=OffPIN

  GPIO.output(SendPIN, 0)
  time.sleep(0.5)
  GPIO.output(SendPIN, 1)
  time.sleep(1)

  GPIO.output(SendPIN, 0)
  time.sleep(0.5)
  GPIO.output(SendPIN, 1)
  time.sleep(1)

  GPIO.output(SendPIN, 0)
  time.sleep(0.5)
  GPIO.output(SendPIN, 1)
  time.sleep(1)

  #Wake fixup
  time.sleep(3)

  log_console(str(heat_op)+" "+str(SendPIN))

  #Power Off
  GPIO.output(PowerPIN, 0)
  GPIO.output(OnPIN, 0)
  GPIO.output(OffPIN, 0)

def log_data(t,p,h):
  global logfile
  try:
    log_file = open(logfile, "a")
    log_file.write(time.strftime("%Y-%m-%d %H:%M")+" "+str(t)+" "+str(p)+" "+str(h)+" "+str (heat_op)+"\n")
    log_file.close()
  except:
    print ("Cannot write to log")

  try:
    tmp_file=open("/tmp/tph", "w+")
    tmp_file.write(str(datetime.datetime.timestamp(datetime.datetime.now()))+","+str(t)+","+str(p)+","+str(h))
    tmp_file.close()
  except:
    print ("Cannot write to temp data file")

  try:
    tmp_file=open("/tmp/ht", "w+")
    tmp_file.write(str(heat_op))
    tmp_file.close()
  except:
    print ("Cannot write to temp data file")

def time_func():
#Once per minute
  global Min_Cycle, heat_counter, heat_op
  global Day_Temp_Min, Day_Temp_Max, Night_Temp_Max, Night_Temp_Min, Away_Temp_Max, Away_Temp_Min, Away_Level
  global last_op, op_count
  s.enter(60, 1, time_func, ())
  try:
    co2file=open("/tmp/co2level","r")
    CO2LEVEL=co2file.read()
    co2file.close()
  except:
    CO2LEVEL=800
  t,p,h=read_bme280()

  #Check for force operations
  if (os.path.isfile(onflag)):
    heat_counter = Force_Cycle
    heat_op = 1
    last_op = -1
    op_count = 0
    #Start the heater
    heater(heat_op)
    os.remove(onflag)
    log_console("Heater forced ON "+str(Force_Cycle))
    log_data(t,p,h)
    return

  if (os.path.isfile(offflag)):
    heat_counter = Force_Cycle
    heat_op = 0
    last_op = -1
    op_count = 0
    #Stop the heater
    heater(heat_op)
    os.remove(offflag)
    log_console("Heater forced OFF "+str(Force_Cycle))
    log_data(t,p,h)
    return

#Let the active operation continue for set cycles
  if (heat_counter > 0):
    heat_counter -= 1
    heater(heat_op)
    log_console("Heater cycle "+str(heat_counter))
    log_data(t,p,h)
    return

#Exit if autocontrol disabled
  if (os.path.isfile(noauto)):
    #log_console("AutoControl is OFF")
    log_data(t,p,h)
    return

#Exit if summer time
  if (not is_winter()):
    #log_console("Summer Time: AutoControl is OFF")
    log_data(t,p,h)
    return

  if (is_night()):
    t_min=Night_Temp_Min
    t_max=Night_Temp_Max
  else:
    t_min=Day_Temp_Min
    t_max=Day_Temp_Max
  if (int(CO2LEVEL) < Away_Level):
    t_min=Away_Temp_Min
    t_max=Away_Temp_Max
  #Now, let's start/stop the heater
  if (t < t_min):
    heat_counter = Min_Cycle
    heat_op = 1
    #Start the heater
    heater(heat_op)
  elif (t > t_max):
    heat_op = 0
    #Stop the heater
    heater(heat_op)
  else:
    heat_op = 2 #Nothing doing
    last_op = -1
    counter = 0
  log_data(t,p,h)

#Let's start
init_bme280()

GPIO.cleanup()
GPIO.setboard(GPIO.ZEROPLUS2H5)    # Orange Pi PC board
GPIO.setmode(GPIO.BOARD)        # set up BOARD BCM numbering
GPIO.setup(PowerPIN, GPIO.OUT)	#Pin 19 - power up transmitter
GPIO.setup(OnPIN, GPIO.OUT)	#Pin 21 - set to LOW to enable heater
GPIO.setup(OffPIN, GPIO.OUT)	#Pin 23 - set to LOW to disable heater

s = sched.scheduler(time.time, time.sleep)
s.enter(1, 1, time_func, ())
s.run()

while True:
    time.sleep(1)

GPIO.cleanup()
