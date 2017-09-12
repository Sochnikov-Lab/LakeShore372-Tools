import serial
import sys
import io
from time import sleep
import numpy as np
from datetime import datetime
from configparser import ConfigParser

argfilename = str(sys.argv[1])

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
