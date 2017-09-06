import serial
import io
from time import sleep
import numpy as np
#import pandas as pd
from datetime import datetime
from configparser import ConfigParser
import LakeShore372 as ls

print("===Debug===")
###Script###
#Open up a serial connection after loading config file:
print("o  Creating LSHDev Object")
LSHDev = ls.LakeShore372Device() #Create and open instance of the LakeShore372 class
print("o  LSHDev Created")
LSHDev.getConfig('config.ini') #Load configuration/ini file
print("o  'config.ini' File loaded")
LSHDev.open() #Open serial port designated in ini file.
print("o  Serial Port Opened")
#print("DevID: " + LSHDev.ID)
print("===========")

print("Device ID: " + LSHDev.getDevID())
print("Resistance of Sample 1: " + str(LSHDev.ReadResistance(LSHDev.sample1)))
LSHDev.close()
