import asyncio
import time
import numpy as np
import PySimpleGUI as sg

##########################################
#Hap device driver
import ser_queue as hdvr

##########################################
#GUI example to control the device

sg.theme('Dark Blue 3')
layout = [
  [sg.T('Miraisense test GUI')],
  [sg.T('BLE',key='BLE',background_color='#333333'),sg.T('HAP'),sg.T('IMU'),sg.T('BAT'),sg.T('---')],
  [sg.Slider(range=(0, 255), orientation='v', size=(5, 20), default_value=0),sg.Slider(range=(-100, 100), orientation='h', size=(20, 20), default_value=0)],
  [sg.B('TEST'),sg.Exit()]
]

window = sg.Window(title='Controller', size=(200, 200)).Layout(layout)

pvalues=""
async def evloop():
  global pvalues
  while True:
    event, values=window.read(timeout=50)
    if event!='__TIMEOUT__': print("event is ",event)
    if event==sg.WIN_CLOSED or event=='Exit':
      queue.put_nowait('Quit')
      break
    elif len(hdvr.events)>0:
      ev=hdvr.events.pop(0)
      if ev=='Connect': window['BLE'].update(background_color='#00FFFF')
    if str(values)!=pvalues:
      print(values,pvalues)
      r=values[0]
      if r>0:
        y=r*values[1]/100
        a=np.arcsin(-y/r)*180/3.1415
        queue.put_nowait('SF I'+str(int(r))+' C'+str(int(a)))
      else:
        queue.put_nowait('SF I0')
      pvalues=str(values)
    await asyncio.sleep(0.05)

##########################################
#Main loop for driving both GUI and BLE
##########################################
async def main():
  global queue
  queue=asyncio.Queue()
  hdvr.queue=queue
  await queue.join()
  task1= asyncio.create_task(evloop())
  task2= asyncio.create_task(hdvr.seloop())
  task3= asyncio.create_task(hdvr.reloop())
  await task1
  await task2
  await task3

asyncio.run(main())
