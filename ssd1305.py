import os, smbus, sched, time, datetime, random, io
import OPi.GPIO as GPIO

SSD1305 = 0x3C
I2CNUM = 0
i2cdev = 0

buffer = bytearray(128*34)
framebuffer = bytearray(128*32>>3)
numbers_big = bytearray(320*32)
drawdots = False

def init_ssd1305():

  global SSD1305, I2CNUM, i2cdev
  global buffer, framebuffer, numbers_big

  buffer = bytearray(128*34)
  framebuffer = bytearray(128*32>>3)

  numbers_big = bytearray(320*32)

  file = open("numbers-1.raw","rb")
  numbers_big = file.read(320*32)
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


def time_func():
  global SSD1305, I2CNUM, i2cdev
  global buffer, framebuffer, numbers_big
  global drawdots

  s.enter(1, 1, time_func, ())

  def putdot(x,y,w):
    bufoffset=y*128+x
    for y in range(w):
      for x in range(w):
        buffer[bufoffset]=0xff
        bufoffset+=1
      bufoffset-=w
      bufoffset+=128

  def putchar(val,bufoffset,charwidth):
    charoffset = val*32
    for x in range(32):
      for y in range(charwidth):
        buffer[bufoffset]=numbers_big[charoffset]
        charoffset+=1
        bufoffset+=1
      charoffset-=charwidth
      bufoffset-=charwidth
      charoffset+=320
      bufoffset+=128

  start_time=time.time()
  #Columns
  i2cdev.write_byte_data(SSD1305, 0x80, 0x21)
  i2cdev.write_byte_data(SSD1305, 0x80, 4)
  i2cdev.write_byte_data(SSD1305, 0x80, 131)
  #Pages
  i2cdev.write_byte_data(SSD1305, 0x80, 0x22)
  i2cdev.write_byte_data(SSD1305, 0x80, 0)
  i2cdev.write_byte_data(SSD1305, 0x80, 3)

  del buffer
  buffer = bytearray(128*34)

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

  #Put buffer to framebuffer
  foffset = 0
  lineconst = 128*7
  for y in range(4):
    rowoffset = y*1024
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
    i2cdev.write_i2c_block_data(SSD1305, 0x40, list(framebuffer[(x<<5):(x<<5)+32]) )
  #print("FPS: ", 1.0 / (time.time() - start_time))

init_ssd1305()

s = sched.scheduler(time.time, time.sleep)
s.enter(1, 1, time_func, ())
s.run()

while True:
  time.sleep(1)

i2cdev.write_byte_data(SSD1305, 0x80, 0xAE)

