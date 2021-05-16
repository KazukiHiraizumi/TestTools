import asyncio
import time
import numpy as np
import serial
import copy 

events=[]
queue=None

PORT=''

async def seloop():
  global ser
  try:
    ser = serial.Serial(PORT,115200,timeout=None)
    ser.timeout=0
    events.append('Connect')
  except Exception:
    print('Connect error')
    exit(1)

  while True:
    cmd = await queue.get()
    print('sdvr queue:',cmd)
    if cmd.startswith('Quit'):
      ser.close()
      break
    ser.write(b'M')
    print('Try IMU reset')
    queue.task_done()
  

rbuf=''
async def reloop():
  global rbuf,events
  while True:
    try:
      b=ser.read(40)
    except Exception:
      break
    if len(b)>0:
      events.append(b.decode('utf-8'))
    await asyncio.sleep(0.01)