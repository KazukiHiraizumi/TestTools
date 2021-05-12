import asyncio
import time
import numpy as np

##########################################
#BLE (Nordic Serial) connection
#  try connecting to the device its name "SPRESENSE"
##########################################
from bleak import BleakClient
from bleak import discover

SVC_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
CWR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
DEV_NAME = "SPRESENSE"

events=[]
queue=None

async def seloop():
  print("Discovering")
  name=DEV_NAME
  devices=await discover()
  target=None 
  for d in devices:
    print(d.address,d.name,d.rssi)
    print(d)
    if name[:4] in d.name:
      target=d
      break
  if target is None:
    print('SPRESENSE not found')
    return
  print("Connecting",target.address)
  async with BleakClient(target.address) as client:
    print("Pairing")
    paired = await client.pair(protection_level=2)
    print("Connected")
    window['BLE'].update(background_color='#00FFFF')
    while True:
        cmd = await queue.get()
        print('CMD:',cmd)
        if cmd=='Quit': break
        await client.write_gatt_char(CWR_UUID,cmd.encode('utf-8'))
        queue.task_done()

async def reloop():
  while True:
    await asyncio.sleep(1)