import asyncio
import time
import numpy as np
import serial

events=[]
queue=None

try:
  ser = serial.Serial('COM6',115200,timeout=None)
  ser.timeout=0
  events.append('Connect')
except Exception:
  exit(1)

norm=0
theta=0
phi=0

def serout(s):
  l=len(s)
  header='$'+format(l+4,'02d')
  ser.write(header.encode('utf-8'))
  ser.write(s.encode('utf-8'))
  sum=0;
  for c in header:
    sum=sum+ord(c)
  for c in s:
    sum=sum+ord(c)
  ser.write(format(sum&0xff,'02x').encode('utf-8'))

def atoi(s):
  try:
    e=s.index(' ')
  except ValueError:
    e=len(s)
  try:
    return int(s[:e])
  except ValueError:
    return None

async def seloop():
  global norm,theta,phi
  while True:
    cmd = await queue.get()
    print('CMD:',cmd)
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
      x=int(x2)+255
      y=int(y2)+255
      z=int(z2)+255
      serout('F0011'+format(x,'03d')+format(y,'03d')+format(z,'03d'))
    queue.task_done()

rbuf=b''
async def reloop():
  global rbuf
  while True:
    try:
      s=ser.read()
    except Exception:
      break
    await asyncio.sleep(0.01)
    if len(s)>0:
      rbuf=rbuf+s
    elif len(rbuf)>0:
      print('REC:',str(rbuf))
      rbuf=b''
