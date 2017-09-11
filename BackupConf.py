import serial
import io
from time import sleep
import numpy as np
from datetime import datetime
from configparser import ConfigParser

#Sets backup INI filename
DataFileName = datetime.now().strftime('%Y%m%d-%H%M%S') + '_LakeShoreConfigBackup' + '.ini' #give it a dated filename

#Open a serial port from commandline argument:
ser = serial.Serial()
ser.timeout = 1 #read timeout --Should fix this to get rid of latency
serIO = io.TextIOWrapper(io.BufferedRWPair(ser,ser),newline="\r\n")
ser.port = SERIALPORT
ser.baudrate = 57600
ser.bytesize = serial.SEVENBITS
ser.parity = serial.PARITY_ODD
ser.stopbits = serial.STOPBITS_ONE
ser.xonxoff = False #Turn off hardware flow control
ser.rtscts = False #Turn off hardware RTS/CTS flow control
ser.dsrdtr = False #Turn off hardware DSR/DTR flow control
ser.open()
serIO.flush()

#Set up the backup INI file
cfp = ConfigParser()
cfp.write(DataFileName)
#Add sample heater section:
cfp.add_section("sampleheater"+str(i))
#Add sections for each channel:
for i in range(0,16):
    cfp.add_section("ch"+str(i))

#Read values for each channel:
enabled = []
tempcoeff = []
curvenumber = []
filterwindow = []
t_dwell = []
t_pause = []
t_settle = []
excitemode = []
excitesetting = []
autoRrange = []
Rrange = []
units = []
autoscan = []

#Read Sample Heater Information:
