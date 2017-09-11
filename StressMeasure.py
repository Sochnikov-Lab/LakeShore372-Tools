import serial
import io
from time import sleep
import numpy as np
#import pandas as pd
from datetime import datetime
from configparser import ConfigParser
import LakeShore372 as ls

def AutorangeSleep1(chdict,maxsleeptime):
    ARsleeptime = 0
    while LSHDev.ReadCHStatus(chdict) != "000" and ARsleeptime < maxsleeptime: #Wait for autoranging to complete
        sleep(1)
        ARsleeptime += 1
    if ARsleeptime >= maxsleeptime:
        print("Slept maximum autorange time, resetting excitation.")
        LSHDev.ExciteOff(chdict)
        sleep(2)
        print()
        LSHDev.Excite(LSHDev.mcthermo)
        sleep(2)
        ARsleeptime = 0
        while LSHDev.ReadCHStatus(chdict) != "000" and ARsleeptime < maxsleeptime: #Wait for autoranging to complete
            sleep(1)
            ARsleeptime += 1
def AutorangeSleep2(chdict,maxsleeptime):
    if LSHDev.ReadCHStatus(chdict) != "000":
        LSHDev.setCHParams(chdict,0)
        sleep(1)
        LSHDev.ExciteOff(chdict)
        sleep(2)
        print()
        LSHDev.setCHParams(chdict,1)
        sleep(1)
        LSHDev.Excite(LSHDev.mcthermo)
        sleep(2)
        ARsleeptime = 0
        while LSHDev.ReadCHStatus(chdict) != "000" and ARsleeptime < maxsleeptime: #Wait for autoranging to complete
            sleep(1)
            ARsleeptime += 1
        if ARsleeptime >= maxsleeptime:
            print("Slept maximum autorange time, resetting excitation.")
            LSHDev.ExciteOff(chdict)
            sleep(2)
            print()
            LSHDev.Excite(LSHDev.mcthermo)
            sleep(2)
            ARsleeptime = 0
            while LSHDev.ReadCHStatus(chdict) != "000" and ARsleeptime < maxsleeptime: #Wait for autoranging to complete
                sleep(1)
                ARsleeptime += 1




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



#next, send one-time configuration over serial:
commandwaittime = 0.5

print("=======Sending One Time Device Configuration======")
sleep(commandwaittime)
#heater:
print(":Sample Heater:")
LSHDev.SetSampleHeaterRange(LSHDev.sampleheater)
print("o  Heater Range SET")
sleep(commandwaittime)
LSHDev.SetSampleHeaterOut(0.0)
LSHDev.HeaterOn()
print("o  Heater Circuit Turned On, heater set to 0.0pc for safety reasons")

#thermometer:
print(":MC Thermometer:")
LSHDev.setCHParams(LSHDev.mcthermo,1) #Set the MC thermometer channel preferences
print("o  Channel Parameters SET")
sleep(commandwaittime)
LSHDev.setFilterParams(LSHDev.mcthermo) #Set the filter prefs for the MC thermometer
print("o  Filter Parameters SET")
sleep(commandwaittime)
LSHDev.Excite(LSHDev.mcthermo) #Sets excitation parameters for MC thermometer
print("o  Excitation Parameters SET")
sleep(commandwaittime)
#sample1:
print(":Sample 1:")
LSHDev.setCHParams(LSHDev.sample1,1)
print("o  Channel Parameters SET")
sleep(commandwaittime)
LSHDev.setFilterParams(LSHDev.sample1)
print("o  Filter Parameters SET")
sleep(commandwaittime)
LSHDev.Excite(LSHDev.sample1) #Sets excitation parameters for MC thermometer
print("o  Excitation Parameters SET")
sleep(commandwaittime)
#sample2:
print(":Sample 2:")
LSHDev.setCHParams(LSHDev.sample2,1)
print("o  Channel Parameters SET")
sleep(commandwaittime)
LSHDev.setFilterParams(LSHDev.sample2)
print("o  Filter Parameters SET")
sleep(commandwaittime)
LSHDev.Excite(LSHDev.sample2) #Sets excitation parameters for MC thermometer
print("o  Excitation Parameters SET")
print("============One Time Configuration Finished==============")

#Open a file to write to, with a description given by the user at runtime.
FileDescription = "Test" #Switch to below statement for full release
#FileDescription = raw_input("What should we call this run's file? ")#Get user description for this run
DataFileName = datetime.now().strftime('%Y%m%d-%H%M%S') + '_' + FileDescription + '.csv' #give it a dated filename
LSHDataFile = open(DataFileName,'w') #Open the file
LSHData = ls.LakeShore372Data(LSHDataFile) #Pass file to data handler class

##Main Loop:
t_safety = 2 #Time to add to delays to allow the LakeShore372 harware to finish first
i = 0 #step number
currentpc = LSHDev.sampleheater["initpc"]
while currentpc < LSHDev.sampleheater["finalpc"]:
    #Set Current
    currentpc = LSHDev.sampleheater["initpc"] + ((i)**(1.0/2.0)) * LSHDev.sampleheater["deltapc"]
    LSHDev.SetSampleHeaterOut(currentpc)
    print("**********New Heater Setting**********")
    print("Current Percentage:" + str(currentpc))
    #Wait Thermalization
    print("Sleeping for Thermalization: " + str(LSHDev.timeConstants["t_therm"]) + " seconds")
    sleep(LSHDev.timeConstants["t_therm"]+t_safety)
    print("Thermalization Over")
    for measurement in range(0,LSHDev.scanner["scannerpasses"]):
        #MC Thermometer
        print(":Scanner: MC Thermometer:")
        LSHDev.Excite(LSHDev.mcthermo)
        sleep(1)
        LSHDev.ScanTo(LSHDev.mcthermo)
        print("o  Sleeping for switch/filter settle: " + str(LSHDev.timeConstants["t_switch"] + LSHDev.mcthermo["t_settle"]) + " seconds")
        sleep(LSHDev.timeConstants["t_switch"] + LSHDev.mcthermo["t_settle"]+t_safety)
        AutorangeSleep2(LSHDev.mcthermo,LSHDev.timeConstants["t_maxARsleep"])
        TempProbeR = LSHDev.ReadResistance(LSHDev.mcthermo)
        print("o  Read Resistance: " + str(TempProbeR) +" Ohms")
        sleep(0.25)
        TempProbeT = LSHDev.ReadKelvin(LSHDev.mcthermo)
        print("o  Read Temperature: " + str(TempProbeT) + " K")
        LSHData.AppendMCThermoK(TempProbeT)
        LSHData.AppendMCThermoR(TempProbeR)
        print("o  Appended Data to arrays")

        #Sample 1
        print(":Scanner: Sample1:")
        LSHDev.Excite(LSHDev.sample1)
        sleep(1)
        LSHDev.ScanTo(LSHDev.sample1)
        print("o  Sleeping for switch/filter settle: " + str(LSHDev.timeConstants["t_switch"] + LSHDev.sample1["t_settle"]) + " seconds")
        sleep(LSHDev.timeConstants["t_switch"] + LSHDev.sample1["t_settle"]+t_safety)
        AutorangeSleep2(LSHDev.sample1,LSHDev.timeConstants["t_maxARsleep"])
        Sample1R = LSHDev.ReadResistance(LSHDev.sample1)
        print("o  Read Resistance: " + str(Sample1R) + " Ohms")
        LSHData.AppendSample1R(Sample1R)
        print("o  Appended Data to arrays")

        #Sample 2
        print(":Scanner: Sample2:")
        LSHDev.Excite(LSHDev.sample2)
        sleep(1)
        LSHDev.ScanTo(LSHDev.sample2)
        print("o  Sleeping for switch/filter settle: " + str(LSHDev.timeConstants["t_switch"] + LSHDev.sample2["t_settle"]) + " seconds")
        sleep(LSHDev.timeConstants["t_switch"] + LSHDev.sample2["t_settle"]+t_safety)
        AutorangeSleep2(LSHDev.sample2,LSHDev.timeConstants["t_maxARsleep"])
        Sample2R = LSHDev.ReadResistance(LSHDev.sample2)
        print("o  Read Resistance: " + str(Sample2R) + " Ohms")
        LSHData.AppendSample2R(Sample2R)
        print("o  Appended Data to arrays")

        #Update CSV
    #    if LSHDataFile.closed:
    #        LSHDataFile.open(DataFileName,'w')
        LSHData.UpdateCSV(currentpc)
    #    LSHDataFile.close() #Close to prevent errors to be proactive about corruption
        LSHData.UpdatePlot(LSHDev.sample1["description"],LSHDev.sample2["description"])
        print("It should be safe to exit for the next 10 seconds: CTRL-C to exit")
        sleep(10)

    ##Loop Back
    i = i + 1

#Turn off heater:
LSHDev.SetSampleHeaterOut(0.0)
LSHDev.HeaterOff()
