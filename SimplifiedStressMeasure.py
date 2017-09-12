#This is a simplified version of the StressMeasure.py script. This version skips the scripted autoconfiguration,
#and relies on the user setting up each channel within the OEM software.
import serial
import io
from time import sleep
import numpy as np
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
#Open a file to write to, with a description given by the user at runtime.
#FileDescription = "Test" #Switch to below statement for full release
FileDescription = raw_input("What should we call this run's file? ")#Get user description for this run
DataFileName = datetime.now().strftime('%Y%m%d-%H%M%S') + '_' + FileDescription + '.csv' #give it a dated filename
LSHDataFile = open(DataFileName,'w') #Open the file
LSHData = ls.LakeShore372Data(LSHDataFile,LSHDev.sample1["description"],LSHDev.sample2["description"],LSHDev.sample3["description"]) #Pass file to data handler class
print("o  Datafile Created.")
print("===========")




LSHDev.SetSampleHeaterRange(LSHDev.sampleheater)
print("o  Heater Range SET")
sleep(0.5)

LSHDev.HeaterOn()
LSHDev.SetSampleHeaterOut(0.35)
sleep(0.05)
LSHDev.SetSampleHeaterOut(0.35)



print("o  Heater Circuit Turned On, heater set to 0.0pc for safety reasons")
print("Number format example: "+"{:.3f}".format(.35))
ht_check=LSHDev.ReadSampleHeater()
sleep(0.05)
print("Heater is confirmed to be set to:" + ht_check)
print("============One Time Configuration Finished==============")



##Main Loop:
t_safety = 7 #Time to add to delays to allow the LakeShore372 harware to finish first
i = 0 #step number
currentpc = LSHDev.sampleheater["initpc"]
while currentpc > LSHDev.sampleheater["finalpc"]:
    #Set Current
    #currentpc = LSHDev.sampleheater["initpc"] + ((i)**(1.0/2.0)) * LSHDev.sampleheater["deltapc"]
    currentpc = LSHDev.sampleheater["initpc"] + i * LSHDev.sampleheater["deltapc"]



    LSHDev.SetSampleHeaterOut(currentpc)
    LSHDev.HeaterOn()


    print("**********New Heater Setting**********")
    print("Current Percentage:" + str(currentpc))
    ht_check=LSHDev.ReadSampleHeater()
    print("Heater is confirmed to be set to:" + ht_check)
    #Wait Thermalization
    print("Sleeping for Thermalization: " + str(LSHDev.timeConstants["t_therm"]) + " seconds")
    sleep(LSHDev.timeConstants["t_therm"]+t_safety)
    print("Thermalization Over")
    for measurement in range(0,LSHDev.scanner["scannerpasses"]):
        #MC Thermometer
        print(":Scanner: MC Thermometer:")
        sleep(1)
        LSHDev.ScanTo(LSHDev.mcthermo)
        print("o  Sleeping for switch/filter settle: " + str(LSHDev.timeConstants["t_switch"] + LSHDev.mcthermo["t_settle"]) + "+ seconds")
        sleep(LSHDev.timeConstants["t_switch"] + LSHDev.mcthermo["t_settle"]+t_safety)
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
        sleep(1)
        LSHDev.ScanTo(LSHDev.sample1)
        print("o  Sleeping for switch/filter settle: " + str(LSHDev.timeConstants["t_switch"] + LSHDev.sample1["t_settle"]) + " seconds")
        sleep(LSHDev.timeConstants["t_switch"] + LSHDev.sample1["t_settle"]+t_safety)
        Sample1R = LSHDev.ReadResistance(LSHDev.sample1)
        print("o  Read Resistance: " + str(Sample1R) + " Ohms")
        LSHData.AppendSample1R(Sample1R)
        print("o  Appended Data to arrays")

        #Sample 2
        print(":Scanner: Sample2:")
        sleep(1)
        LSHDev.ScanTo(LSHDev.sample2)
        print("o  Sleeping for switch/filter settle: " + str(LSHDev.timeConstants["t_switch"] + LSHDev.sample2["t_settle"]) + " seconds")
        sleep(LSHDev.timeConstants["t_switch"] + LSHDev.sample2["t_settle"]+t_safety)
        Sample2R = LSHDev.ReadResistance(LSHDev.sample2)
        print("o  Read Resistance: " + str(Sample2R) + " Ohms")
        LSHData.AppendSample2R(Sample2R)
        print("o  Appended Data to arrays")

        #Sample 3
        print(":Scanner: Sample3:")
        sleep(1)
        LSHDev.ScanTo(LSHDev.sample3)
        print("o  Sleeping for switch/filter settle: " + str(LSHDev.timeConstants["t_switch"] + LSHDev.sample3["t_settle"]) + " seconds")
        sleep(LSHDev.timeConstants["t_switch"] + LSHDev.sample3["t_settle"]+t_safety)
        Sample3R = LSHDev.ReadResistance(LSHDev.sample3)
        print("o  Read Resistance: " + str(Sample3R) + " Ohms")
        LSHData.AppendSample3R(Sample3R)
        print("o  Appended Data to arrays")

        #Update CSV
    #    if LSHDataFile.closed:
    #        LSHDataFile.open(DataFileName,'w')
        LSHData.UpdateCSV(currentpc)
    #    LSHDataFile.close() #Close to prevent errors to be proactive about corruption
        LSHData.UpdatePlot(LSHDev.sample1["description"],LSHDev.sample2["description"],LSHDev.sample3["description"])
        print("It should be safe to exit for the next 2 seconds: CTRL-C to exit")
        sleep(2)

    ##Loop Back
    i = i + 1

#Turn off heater:
LSHDev.SetSampleHeaterOut(0.0)
LSHDev.HeaterOff()
