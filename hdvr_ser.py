import asyncio
import time
import numpy as np
import serial

events=[]
queue=None

PORT=''

norm=0
theta=0
phi=0
x1=0.0
y1=0.0
z1=0.0
w1=1.0
x2=0
y2=0
z2=0

def setquat(quat):
  global x1,y1,z1,w1
  x1=quat[0]
  y1=quat[1]
  z1=quat[2]
  w1=quat[3]
  update()

def serout(s):
  l=len(s)
  header=('$'+format(l+4,'02d')).encode('utf-8')
  ser.write(header)
#  print("header",header)
  body=s.encode('utf-8');
  ser.write(body)
#  print("body",body)
  smn=0
  for ch in list(header)[1:]:
#    print(format(ch,'02x'),smn)
    smn=smn+ch
  for ch in list(body):
#    print(format(ch,'02x'),smn)
    smn=smn+ch
  ssm=format(smn&0xff,'02X').encode('utf-8')
  print("serout",header,body,ssm)
  ser.write(ssm)
  ser.write(b';')

def atoi(s):
  try:
    e=s.index(' ')
  except ValueError:
    e=len(s)
  try:
    return int(s[:e])
  except ValueError:
    return None

def update():
  x0=(x1*x2+y1*y2+z1*z2)*x1+w1*(w1*x2-y1*y2+z1*z2)+(w1*y2-z1*x2+x1*z2)*z1-(w1*z2-x1*y2+y1*x2)*y1
  y0=(x1*x2+y1*y2+z1*z2)*y1+w1*(w1*y2-z1*x2+x1*z2)+(w1*z2-x1*y2+y1*x2)*x1-(w1*x2-y1*y2+z1*z2)*z1
  z0=(x1*x2+y1*y2+z1*z2)*z1+w1*(w1*y2-z1*x2+x1*z2)+(w1*x2-y1*y2+z1*z2)*y1-(w1*y2-z1*x2+x1*z2)*x1
  xi=int(x0)
  yi=int(y0)
  zi=int(z0)
  print('update',x1,y1,z1,w1,'|',x2,y2,z2,'|',xi,yi,zi)
  serout('F0011'+format(xi+255,'03d')+format(yi+255,'03d')+format(zi+255,'03d'))

def connect():
  global ser
  try:
    ser = serial.Serial(PORT,115200,timeout=None)
    ser.timeout=0
    events.append('Connect')
  except Exception:
    print('Connect error')
    exit(1)

async def seloop():
  global ser,norm,theta,phi,x2,y2,z2
  connect()

  while True:
    cmd = await queue.get()
    print('hdvr queue:',cmd)
    if cmd.startswith('Quit'):
      ser.close()
      break
    elif cmd.startswith('SF'):
      try:
        si=cmd.index('I')
        norm=atoi(cmd[si+1:])
      except ValueError:
        pass
      try:
        sc=cmd.index('C')
        theta=atoi(cmd[sc+1:])*3.1415/180
      except ValueError:
        pass
      try:
        sb=cmd.index('B')
        phi=atoi(cmd[sb+1:])*3.1415/180
      except ValueError:
        pass
      x2=norm*np.cos(phi)*np.cos(theta)
      y2=norm*np.cos(phi)*np.sin(theta)
      z2=norm*np.sin(phi)
      try:
        ss=cmd.index('X')
        x2=atoi(cmd[ss+1:])
      except ValueError:
        pass
      try:
        ss=cmd.index('Y')
        y2=atoi(cmd[ss+1:])
      except ValueError:
        pass
      try:
        ss=cmd.index('Z')
        z2=atoi(cmd[ss+1:])
      except ValueError:
        pass
      update()
    queue.task_done()

async def reloop():
  while True:
    try:
      s=ser.read(100)
    except Exception:
      break
    if len(s)>0:
      print('hdrv read',s)
    await asyncio.sleep(0.01)
