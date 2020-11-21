import os, smbus, sched, time, datetime, random, io, threading, socket
import OPi.GPIO as GPIO

SSD1305 = 0x3C
I2CNUM = 0
i2cdev = 0

UDP_IP = "192.168.0.140"
UDP_PORT = 4000

buffer = bytearray(128*34)
framebuffer = bytearray(128*32>>3)
numbers_big = bytearray(480*32)
drawdots = False
exp = 5
cycles = exp
first_trans = False

tph_file = "/tmp/tph"
co2_file = "/tmp/co2level"
heat_file = "/tmp/heating"

cdate = 0
heating = False
t = 0
p = 0
h = 0
co2 = 0

def init_ssd1305():

  global SSD1305, I2CNUM, i2cdev
  global buffer, framebuffer, numbers_big

  buffer = bytearray(128*34)
  framebuffer = bytearray(128*32>>3)

  numbers_big = bytearray(480*32)

  file = open("numbers-1.raw","rb")
  numbers_big = file.read(480*32)
  file.close

  i2cdev = smbus.SMBus(I2CNUM)

  #On
  i2cdev.write_byte_data(SSD1305, 0x80, 0xAF)

  #MUX / number of lines
  i2cdev.write_byte_data(SSD1305, 0x80, 0xA8)
  i2cdev.write_byte_data(SSD1305, 0x80, 31)

  #Horisontal addressing mode
  i2cdev.write_byte_data(SSD1305, 0x80, 0x20)
  i2cdev.write_byte_data(SSD1305, 0x80, 0x0)

  #Reverse/set orientation
  i2cdev.write_byte_data(SSD1305, 0x80, 0xC8)
  i2cdev.write_byte_data(SSD1305, 0x80, 0xA1)

  #Columns
  i2cdev.write_byte_data(SSD1305, 0x80, 0x21)
  i2cdev.write_byte_data(SSD1305, 0x80, 4)
  i2cdev.write_byte_data(SSD1305, 0x80, 131)

  #Pages
  i2cdev.write_byte_data(SSD1305, 0x80, 0x22)
  i2cdev.write_byte_data(SSD1305, 0x80, 0)
  i2cdev.write_byte_data(SSD1305, 0x80, 3)

#clean
  for x in range(128*32>>3):
   i2cdev.write_byte_data(SSD1305, 0x40, 0 )

  #Columns
  i2cdev.write_byte_data(SSD1305, 0x80, 0x21)
  i2cdev.write_byte_data(SSD1305, 0x80, 4)
  i2cdev.write_byte_data(SSD1305, 0x80, 131)

  #Pages
  i2cdev.write_byte_data(SSD1305, 0x80, 0x22)
  i2cdev.write_byte_data(SSD1305, 0x80, 0)
  i2cdev.write_byte_data(SSD1305, 0x80, 3)

  i2cdev.write_byte_data(SSD1305, 0x80, 0x81)
  i2cdev.write_byte_data(SSD1305, 0x80, 0x0)

def putdot(x,y,w):
  global buffer, framebuffer, numbers_big
  bufoffset=y*128+x
  for y in range(w):
    for x in range(w):
      buffer[bufoffset]=0xff
      bufoffset+=1
    bufoffset-=w
    bufoffset+=128

def putchar(val,bufoffset,charwidth):
  global buffer, framebuffer, numbers_big
  charoffset = val*32
  for x in range(32):
    for y in range(charwidth):
      buffer[bufoffset]=numbers_big[charoffset]
      charoffset+=1
      bufoffset+=1
    charoffset-=charwidth
    bufoffset-=charwidth
    charoffset+=480
    bufoffset+=128

def render():
  global buffer, framebuffer
  #Move pointer to start
  #Columns
  i2cdev.write_byte_data(SSD1305, 0x80, 0x21)
  i2cdev.write_byte_data(SSD1305, 0x80, 4)
  i2cdev.write_byte_data(SSD1305, 0x80, 131)
  #Pages
  i2cdev.write_byte_data(SSD1305, 0x80, 0x22)
  i2cdev.write_byte_data(SSD1305, 0x80, 0)
  i2cdev.write_byte_data(SSD1305, 0x80, 3)
  #Put buffer to framebuffer
  foffset = 0
  lineconst = 7<<7
  for y in range(4):
    rowoffset = y<<10
    for x in range(128):
      xoff = x+rowoffset+lineconst
      pixel = (buffer[xoff]>>7)
      for z in range(7):
        xoff-=128
        pixel=pixel<<1
        pixel = pixel | (buffer[xoff]>>7)
      framebuffer[foffset] = pixel & 0xff
      foffset += 1
  for x in range(16):
    i2cdev.write_i2c_block_data(SSD1305, 0x40, list(framebuffer[(x<<5):(x<<5)+32]))

def render_slow():
  global buffer, framebuffer
  #Move pointer to start
  #Columns
  i2cdev.write_byte_data(SSD1305, 0x80, 0x21)
  i2cdev.write_byte_data(SSD1305, 0x80, 4)
  i2cdev.write_byte_data(SSD1305, 0x80, 131)
  #Pages
  i2cdev.write_byte_data(SSD1305, 0x80, 0x22)
  i2cdev.write_byte_data(SSD1305, 0x80, 0)
  i2cdev.write_byte_data(SSD1305, 0x80, 3)
  #Put buffer to framebuffer
  foffset = 0
  lineconst = 7<<7
  for y in range(4):
    rowoffset = y<<10
    for x in range(128):
      xoff = x+rowoffset+lineconst
      pixel = (buffer[xoff]>>7)
      for z in range(7):
        xoff-=128
        pixel=pixel<<1
        pixel = pixel | (buffer[xoff]>>7)
      framebuffer[foffset] = pixel & 0xff
      foffset += 1

  for x in range(16):
    i2cdev.write_i2c_block_data(SSD1305, 0x40, list(framebuffer[(x<<5):(x<<5)+32]))
    time.sleep(0.01)

#Read all data once per minute
def vals_func():
  global tph_file, co2_file, heatfile
  global cdate,t,p,h,co2,heating
  s.enter(60, 1, vals_func, ())
  #Get TPH
  try:
    tphfile=open(tph_file,"r")
    data=tphfile.read()
    tphfile.close()
    cdate,t,p,h=map(float,data.split(","))
    cdate=datetime.datetime.fromtimestamp(cdate)
  except:
    t=20
    p=985 #Earth avg from wiki
    h=50
    cdate=datetime.datetime.now()
  try:
    tphfile=open(co2_file,"r")
    co2=tphfile.read()
    tphfile.close()
  except:
    co2=800
  heating = os.path.isfile(heat_file)
  #print(cdate,t,p,h,co2,heating)

def co2_func():
  global SSD1305, I2CNUM, i2cdev
  global buffer, framebuffer, first_trans,exp
  global drawdots, cycles, t, p, h, co2, heating
  del buffer
  buffer = bytearray(128*32)
  first_trans = (cycles == exp)
  cycles-=1
  if (cycles > 0):
    s.enter(1, 1, co2_func, ())
  else:
    s.enter(1, 1, humi_func, ())
    cycles = exp

  temp = int(co2)

  val = (temp // 1000)
  bufoffset = 0
  if (val > 0):
    putchar(val,bufoffset,28)

  val = (temp // 100) % 10
  bufoffset = 28+2
  putchar(val,bufoffset,28)

  val = (temp // 10) % 10
  bufoffset = 28+2+28+2
  putchar(val,bufoffset,28)

  val = temp % 10
  bufoffset = 28+2+28+2+28+2
  putchar(val,bufoffset,28)

  bufoffset=119
  putchar(13,bufoffset,9)

  if first_trans:
    render_slow()
    first_trans = False
  else:
    render()

def humi_func():
  global SSD1305, I2CNUM, i2cdev
  global buffer, framebuffer, first_trans,exp
  global drawdots, cycles, t, p, h, co2, heating
  del buffer
  buffer = bytearray(128*32)
  first_trans = (cycles == exp)
  cycles-=1
  if (cycles > 0):
    s.enter(1, 1, humi_func, ())
  else:
    s.enter(1, 1, pres_func, ())
    cycles = exp

  temp = int(h)

  val = (temp // 100)
  bufoffset = 0
  if (val > 0):
    putchar(val,bufoffset,28)

  val = (temp // 10) % 10
  bufoffset = 31
  putchar(val,bufoffset,28)

  val = temp % 10
  bufoffset = 63
  putchar(val,bufoffset,28)

  bufoffset=127-32
  putchar(14,bufoffset,32)

  if first_trans:
    render_slow()
    first_trans = False
  else:
    render()

def pres_func():
  global SSD1305, I2CNUM, i2cdev
  global buffer, framebuffer, first_trans,exp
  global drawdots, cycles, t, p, h, co2, heating
  del buffer
  buffer = bytearray(128*32)
  first_trans = (cycles == exp)
  cycles-=1
  if (cycles > 0):
    s.enter(1, 1, pres_func, ())
  else:
    s.enter(1, 1, time_func, ())
    cycles = exp

  temp = int(p)

  val = (temp // 1000)
  bufoffset = 0
  if (val > 0):
    putchar(val,bufoffset,28)

  val = (temp // 100) % 10
  bufoffset = 28+2
  putchar(val,bufoffset,28)

  val = (temp // 10) % 10
  bufoffset = 28+2+28+2
  putchar(val,bufoffset,28)

  val = temp % 10
  bufoffset = 28+2+28+2+28+2
  putchar(val,bufoffset,28)

  bufoffset=119
  putchar(12,bufoffset,9)

  if first_trans:
    render_slow()
    first_trans = False
  else:
    render()


def temp_func():
  global SSD1305, I2CNUM, i2cdev
  global buffer, framebuffer, first_trans,exp
  global drawdots, cycles, t, p, h, co2, heating
  del buffer
  buffer = bytearray(128*32)
  first_trans = (cycles == exp)
  cycles-=1
  if (cycles > 0):
    s.enter(1, 1, temp_func, ())
  else:
    s.enter(1, 1, co2_func, ())
    cycles = exp
  temp = int(round(t*10))
  val = temp // 100
  bufoffset = 0
  if (val > 0):
    putchar(val,bufoffset,28)
  val = (temp % 100) // 10
  bufoffset = 30
  putchar(val,bufoffset,28)
  val = (temp % 10)
  bufoffset = 70
  putchar(val,bufoffset,28)
  putdot(61,27,4)

  if (heating):
    bufoffset = 98
    putchar(11,bufoffset,28)
  else:
    bufoffset = 70+34
    putchar(10,bufoffset,20)

  if first_trans:
    render_slow()
    first_trans = False
  else:
    render()


def time_func():
  global SSD1305, I2CNUM, i2cdev
  global buffer, framebuffer, first_trans, exp
  global drawdots, cycles

  first_trans = (cycles == exp)

  cycles-=1
  if (cycles > 0):
    s.enter(1, 1, time_func, ())
  else:
    s.enter(1, 1, temp_func, ())
    cycles = exp

  #FPS start_time=time.time()

  del buffer
  buffer = bytearray(128*32)

  now = datetime.datetime.now()

  val = now.hour // 10
  bufoffset = 0
  if (val > 0):
    putchar(val,bufoffset,28)

  val = now.hour % 10
  bufoffset = 28+1
  putchar(val,bufoffset,28)

  val = now.minute // 10
  bufoffset = 64+8-1
  putchar(val,bufoffset,28)

  val = now.minute % 10
  bufoffset = 64+8+28
  putchar(val,bufoffset,28)

  drawdots = not drawdots
  if drawdots:
    putdot(61,12,4)
    putdot(61,20,4)

  if first_trans:
    render_slow()
    first_trans = False
  else:
    render()

  #FPS print("FPS: ", 1.0 / (time.time() - start_time))

def udprec():
  global UDP_IP, UDP_PORT
  global cdate,t,p,h,co2,heating
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind((UDP_IP, UDP_PORT))
  while True:
    data, addr = sock.recvfrom(256)
    if data[0:8] == b'climdata':
      clim = data.decode().split(",")
      cdate = datetime.datetime.fromtimestamp(float(clim[1]))
      t = float(clim[2])
      p = float(clim[3])
      h = float(clim[4])
      co2 = int(clim[5])
      heating = bool(int(clim[6]))
      #print (t,p,h,co2,clim[6],heating)
  sock.close()

UDP_REC = threading.Thread(target=udprec)
UDP_REC.start()

init_ssd1305()

s = sched.scheduler(time.time, time.sleep)
s.enter(1, 1, time_func, ())
#s.enter(1, 1, vals_func, ())
s.run()

while True:
  time.sleep(1)

i2cdev.write_byte_data(SSD1305, 0x80, 0xAE)

