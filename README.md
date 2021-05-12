# TestTools

## 準備

### Bleak
BLEライブラリ
注意！Pythonは3.8以降でないとエラーとなります。
インストール
~~~
pip install bleak
~~~
テストプログラムはbl.pyです。アドバタイズビーコンのDiscoveryを行います。
~~~
python bl.py
~~~
マルチバージョン環境で強制で3.8で起動する
~~~
py -3.8 bl.py
~~~

### PySimpleGUI  
新しいPythonのGUIフレームワーク
~~~
pip install pysinplegui
~~~
マルチバージョン環境ではインストールに注意ください
~~~
py -3.8 -m pip install pysimplegui
~~~

### PySerial  
シリアルポートI/O

## 準備
- hapt_ser.py  
Serial port接続にてデバイスのテストする
- hapt_nus.py  
NUS(Nordic UART Service)接続にてデバイスのテストする