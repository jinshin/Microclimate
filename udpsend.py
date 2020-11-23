import os,socket,time,datetime,sched

UDP_IP = "192.168.0.140"
UDP_PORT = 4000
ID = 1

tph_file = "/tmp/tph"
co2_file = "/tmp/co2level"
heat_file = "/tmp/heating"

def vals_func():
  global tph_file, co2_file, heatfile, ID
  s.enter(30, 1, vals_func, ())
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
  sendstr = "climdata,%f,%d,%f,%f,%f,%d,%d" % (time.mktime(cdate.timetuple()),ID,t,p,h,int(co2),int(heating))
  #print(sendstr)
  MESSAGE = str.encode(sendstr)
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

s = sched.scheduler(time.time, time.sleep)
s.enter(1, 1, vals_func, ())
s.run()

while True:
  time.sleep(1)
