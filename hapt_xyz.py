import asyncio
import time
import numpy as np
import PySimpleGUI as sg

##########################################
#Hap device driver
import hdvr_ser as hdvr
hdvr.PORT='COM9'

##########################################
#Spresense serial driver
import sdvr_ser as sdvr
sdvr.PORT='COM5'

##########################################
#GUI example to control the device

sg.theme('Dark Blue 3')
layout = [
  [sg.T('Miraisense test GUI')],
  [sg.T('HAP',key='connHap',background_color='#333333'),sg.T('IMU',key='connImu',background_color='#333333'),sg.T('GPS',key='connGps',background_color='#333333'),sg.T('BAT',key='connBat',background_color='#333333')],
  [sg.Slider(range=(-255, 255), orientation='h', size=(10, 20), default_value=0,key='X'),sg.Slider(range=(-255, 255), orientation='v', size=(5, 20), default_value=0,key='Y'),sg.Slider(range=(-255, 255), orientation='v', size=(5, 20), default_value=0,key='Z'),sg.B('Zero',key='setZero')],
  [sg.Exit()]
]

window = sg.Window(title='Controller', size=(300, 200)).Layout(layout)

pvalues={'X':0,'Y':0,'Z':0}
async def evloop():
  global pvalues
  while True:
    event, values=window.read(timeout=50)
    if event!='__TIMEOUT__': print("window event ",event)
    if event==sg.WIN_CLOSED or event=='Exit':
      hqueue.put_nowait('Quit')
      squeue.put_nowait('Quit')
      break
    elif event=='setZero':
      window['X'].update(value=0)
      window['Y'].update(value=0)
      window['Z'].update(value=0)
    elif len(hdvr.events)>0:
      ev=hdvr.events.pop(0)
      if ev=='Connect': window['connHap'].update(background_color='#0044FF')
    elif len(sdvr.events)>0:
      ev=sdvr.events.pop(0)
      if ev=='Connect': window['connImu'].update(background_color='#0044FF')
      elif ev.startswith('['):
        try:
          quat=eval(ev)
          hdvr.setquat(quat)
        except Exception as e:
          print('eval err',e)
    else:
      cmd=''
      for key in values:
        if pvalues[key] !=  values[key]:
          cmd=cmd+key+str(int(values[key]))+' '
      pvalues=values
      if len(cmd)>0:
        hqueue.put_nowait('SF '+cmd)
    await asyncio.sleep(0.01)

##########################################
#Main loop for driving both GUI and BLE
##########################################
async def main():
  global hqueue,squeue
  hqueue=asyncio.Queue()
  squeue=asyncio.Queue()
  hdvr.queue=hqueue
  sdvr.queue=squeue
  task1= asyncio.create_task(evloop())
  task2= asyncio.create_task(hdvr.seloop())
  task3= asyncio.create_task(hdvr.reloop())
  task4= asyncio.create_task(sdvr.seloop())
  task5= asyncio.create_task(sdvr.reloop())
  await task1
  await task2
  await task3
  await task4
  await task5

asyncio.run(main())
