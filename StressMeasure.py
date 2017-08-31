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
print("DevID: " + LSHDev.ID)
print("===========")

#Open a file to write to, with a description given by the user at runtime.
FileDescription = raw_input("What should we call the file? ")#Get user description for this run
DataFileName = datetime.now().strftime('%Y%m%d-%H%M%S') + '_' + FileDescription + '.csv' #give it a dated filename
LSHDataFile = open(DataFileName,'w') #Open the file
LSHData = ls.LakeShore372Data(LSHDataFile) #Pass file to data handler class

#next, send one-time configuration over serial:
print("=======OneTimeConfig======")

#heater:
print(":Sample Heater:")
LSHDev.SetSampleHeaterRange(LSHDev.sampleheater)
print("o  Heater Range SET")
sleep(0.25)
#thermometer:
print(":MC Thermometer:")
LSHDev.setCHParams(LSHDev.mcthermo,1) #Set the MC thermometer channel preferences
print("o  Channel Parameters SET")
sleep(0.25)
LSHDev.setFilterParams(LSHDev.mcthermo) #Set the filter prefs for the MC thermometer
print("o  Filter Parameters SET")
sleep(0.25)
LSHDev.Excite(LSHDev.mcthermo) #Sets excitation parameters for MC thermometer
print("o  Excitation Parameters SET")
sleep(0.25)
#sample1:
print(":Sample 1:")
LSHDev.setCHParams(LSHDev.sample1,1)
print("o  Channel Parameters SET")
sleep(0.25)
LSHDev.setFilterParams(LSHDev.sample1)
print("o  Filter Parameters SET")
sleep(0.25)
LSHDev.Excite(LSHDev.sample1) #Sets excitation parameters for MC thermometer
print("o  Excitation Parameters SET")
sleep(0.25)
#sample2:
print(":Sample 2:")
LSHDev.setCHParams(LSHDev.sample2,1)
print("o  Channel Parameters SET")
sleep(0.25)
LSHDev.setFilterParams(LSHDev.sample2)
print("o  Filter Parameters SET")
sleep(0.25)
LSHDev.Excite(LSHDev.sample2) #Sets excitation parameters for MC thermometer
print("o  Excitation Parameters SET")
sleep(0.25)
print("==========================")

print(".")


##Main Loop:
i = 0 #step number
currentpc = LSHDev.sampleheater["initpc"]
while currentpc < LSHDev.sampleheater["finalpc"]:
    #Set Current
    currentpc = LSHDev.sampleheater["initpc"] + ((i)**(1.0/2.0)) * LSHDev.sampleheater["deltapc"]
    print("Current Percentage:" + str(currentpc))
    #Wait Thermalization
    print("Sleeping for Thermalization: " + str(LSHDev.timeConstants["t_therm"]) + " seconds")
    sleep(LSHDev.timeConstants["t_therm"])
    print("Thermalization Over")
    for measurement in range(0,LSHDev.scanner["scannerpasses"]):
        #MC Thermometer
        print(":Scanner: MC Thermometer:")
        LSHDev.ScanTo(LSHDev.mcthermo)
        print("o  Sleeping for switch/filter settle: " + str(LSHDev.timeConstants["t_switch"] + LSHDev.mcthermo["t_settle"]) + " seconds")
        sleep(LSHDev.timeConstants["t_switch"] + LSHDev.mcthermo["t_settle"])
        #Scan to Temp Probe, Read Temp Probe T/R
        TempProbeT = LSHDev.ReadKelvin(LSHDev.mcthermo)
        print("o  Read Temperature")
        sleep(0.25)
        TempProbeR = LSH.ReadResistance(LSHDev.mcthermo)
        print("o  Read Resistance")
        LSHData.AppendMCThermoK(TempProbeT)
        LSHData.AppendMCThermoR(TempProbeR)
        print("o  Appended Data to arrays")

        #Sample 1
        print(":Scanner: Sample1:")
        LSHDev.ScanTo(LSHDev.sample1)
        print("o  Sleeping for switch/filter settle: " + str(LSHDev.timeConstants["t_switch"] + LSHDev.mcthermo["t_settle"]) + " seconds")
        sleep(LSHDev.timeConstants["t_switch"] + LSHDev.sample1["t_settle"])
        Sample1R = LSHDev.ReadResistance(LSHDev.sample1)
        print("o  Read Resistance: " + str(Sample1R) + " Ohms")
        LSHData.AppendSample1R(Sample1R)
        print("o  Appended Data to arrays")

        #Sample 2
        print(":Scanner: Sample1:")
        LSHDev.ScanTo(LSHDev.sample2)
        print("o  Sleeping for switch/filter settle: " + str(LSHDev.timeConstants["t_switch"] + LSHDev.mcthermo["t_settle"]) + " seconds")
        sleep(LSHDev.timeConstants["t_switch"] + LSHDev.sample2["t_settle"])
        Sample2R = LSHDev.ReadResistance(LSHDev.sample2)
        print("o  Read Resistance: " + str(Sample1R) + " Ohms")
        LSHData.AppendSample2R(Sample2R)
        print("o  Appended Data to arrays")

        #Update CSV
        LSHData.UpdateCSV(currentpc)
        LSHData.UpdatePlot()
    ##Loop Back
    i = i + 1
