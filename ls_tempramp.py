import serial
import io
import time
import numpy as np
import pandas as pd
from datetime import datetime
from configparser import ConfigParser

###LakeShore AC/Resistance Bridge Class###
class LakeShore372(object):
    #Initialization: create necessary variables and configurable serial instance
    def __init__(self):
        self.ID = ''         #ID of instrument
        self.ready = False   #If device is ready for command
        self.ser = serial.Serial() #Serial Instance
        self.ser.timeout = 0.25 #read timeout --Should fix this to get rid of latency
        self.serIO = io.TextIOWrapper(io.BufferedRWPair(self.ser,self.ser),newline='\r\n')
    #Attempts to open serial instance
    def open(self,COMPORT,BAUDRATE=115200,verbose=0):
        try:
            self.ser.port = COMPORT
            self.ser.baudrate = BAUDRATE
            self.ser.open()
            #Read ID from Serial Port:
            self.serIO.write(unicode('*IDN?\r'))
            self.serIO.flush()
            self.ID = str(self.serIO.readline()).rstrip().lstrip()
        except serial.SerialException:
            print("**Failed to open serial port**")

    def close(self,verbose=0):
        try:
            self.ser.close()
        except serial.SerialException:
            print("**Failed to close serial port**")
    def ReadCHStatus(self,CH):
        self.serIO.write(unicode('RDGST?' + str(CH) + '\r'))
        self.serIO.flush()
        return str(self.serIO.readline()).rstrip().lstrip()
    def ReadResistance(self,CH):
        self.serIO.write(unicode('RDGR?' + str(CH) + '\r'))
        self.serIO.flush()
        return float(str(self.serIO.readline()).rstrip().lstrip())
    def ReadKelvin(self,CH):
        self.serIO.write(unicode('RDGK?' + str(CH) + '\r'))
        self.serIO.flush()
        return float(str(self.serIO.readline()).rstrip().lstrip())
    def ScanTo(self,CH,AUTOSCAN):
        self.serIO.write(unicode('SCAN' + str(CH) + ',' + str(AUTOSCAN) + '\r'))
        self.serIO.flush()
        #return float(str(self.serIO.readline()).rstrip().lstrip())
    def SetSampleHeaterCurrent(self,RESISTANCE,MAXCURR,DISP):
        self.serIO.write(unicode('HTRSET0,' + str(RESISTANCE) + ',0,' + str(MAXCURR) + ',' + str(DISP) + '\r'))
        self.serIO.flush()
        #return float(str(self.serIO.readline()).rstrip().lstrip())
    def SetSampleHeaterRange(self,RANGE):
        self.serIO.write(unicode('RANGE0,' + str(RANGE) + '\r'))
        self.serIO.flush()

#Data Handler Class (Saves/Plots data)
class LakeShore372Data(object):
    def __init__(self,DataFile):
        #Lists of Resistances / Temperatures
        self.ThermoR = []
        self.ThermoK = []
        self.ControlR = []
        self.StressR = []
        #Last Read Value:
        self.ThermoRL = 0.0
        self.ThermoKL = 0.0
        self.ControlRL = 0.0
        self.StressRL = 0.0
        #CSV file
        self.DataFile = DataFile
        #Write Header:
        self.DataFile.write("TTemp,TResist,CResist,SResist\n")



    def AppendThermoR(self,RReading):
        self.ThermoRL = RReading
        self.ThermoR.append(RReading)
    def AppendThermoK(self,KReading):
        self.ThermoRK = RReading
        self.ThermoK.append(KReading)
    def AppendControlR(self,RReading):
        self.ControlRL = RReading
        self.ControlR.append(RReading)
    def AppendStressR(self,RReading):
        self.StressRL = RReading
        self.StressR.append(RReading)
    def UpdateCSV(self):
        self.DataFile.write(str(self.ThermoKL) + ',' +str(self.ThermoRL) + ',' +str(self.ControlRL) + ',' +str(self.StressRL) + '\n')
    def UpdatePlot(self):
        print("muh plot")

###Script###

###Configuration INI file / Dictionaries###
cfgparser = ConfigParser()
cfgparser.read('config.ini')
#Connection configuration
serial_cfg = {
    "port":str(cfgparser.get('connection','serialport')),
    "baud":int(cfgparser.get('connection','baudrate'))
}
#sample heater configuration
#resistance: Ohms
#maxCurrent: A
#range: mA
sh_cfg = {
    "resistance":float(cfgparser.get('sampleheater','resistanceOhms')),
    "maxcurrent":float(cfgparser.get('sampleheater','maxcurrentAmps')),
    "range":float(cfgparser.get('sampleheater','range')),
    "disp":int(cfgparser.get('sampleheater','disp')),
    "initpc":float(cfgparser.get('sampleheater','initpc')),
    "finalpc":float(cfgparser.get('sampleheater','finalpc')),
    "stepsizepc":int(cfgparser.get('sampleheater','steps'))
}
#Scanner Configuration
scanner_cfg = {
    "thermo":int(cfgparser.get('scanner','thermo_ch')),
    "control":int(cfgparser.get('scanner','control_ch')),
    "stress":int(cfgparser.get('scanner','stress_ch')),
    "autoscan":int(cfgparser.get('scanner','autoscan'))
}
#Timing
timing_cfg = {
    "timeconst":float(cfgparser.get('timeconstants','t_therm')),
    "thermal":float(cfgparser.get('timeconstants','t_const')),
    "switch":float(cfgparser.get('timeconstants','t_switch')),
    "settle":float(cfgparser.get('timeconstants','t_settle'))
}


#First, create and open instance of the LakeShore372 class:
LSH = LakeShore372()
LSH.open()
#Second, Create Instance of the data handler class and a datafile:
FileDescription = raw_input("What should we call the file? ")
DateStr = datetime.now().strftime('%Y%m%d%-H%M%S')
DataFileName = DateStr + '_' + FileDescription + '.csv'
LSHDataFile = open(DataFileName,'w')
LSHData = LakeShore372Data(LSHDataFile)

#next, send one-time configuration over serial:
LSH.SetSampleHeaterRange(sh_cfg["range"])


##Main Loop:
i = 0 #step number

while currentpc < sh_cfg["finalpc"]:
    #Set Current
    currentpc = sh_cfg["initpc"] + ((i)**(1.0/2.0)) * sh_cfg["stepsizepc"]
    #Wait Thermalization
    sleep(timing_cfg["thermal"])
    #Wait (Other)
    sleep(timing_cfg["timeconst"] + timing_cfg["switch"] + timing_cfg["settle"])
    #Scan to Temp Probe, Read Temp Probe T/R
    LSH.ScanTo(scanner_cfg["thermo"],scanner_cfg["autoscan"])
    TempProbeT = LSH.ReadKelvin(scanner_cfg["thermo"])
    sleep(timing_cfg["settle"])
    TempProbeR = LSH.ReadResistance(scanner_cfg["thermo"])
    #Wait (Other)
    sleep(timing_cfg["timeconst"] + timing_cfg["switch"] + timing_cfg["settle"])
    #Scan to Control Sample, Read R
    LSH.ScanTo(scanner_cfg["control"],scanner_cfg["autoscan"])
    ControlR = LSH.ReadResistance(scanner_cfg["control"])
    #Wait (Other)
    sleep(timing_cfg["timeconst"] + timing_cfg["switch"] + timing_cfg["settle"])
    #Scan to Stressed Sample, Read R
    LSH.ScanTo(scanner_cfg["stress"],scanner_cfg["autoscan"])
    StressR = LSH.ReadResistance(scanner_cfg["stress"])
    #Append values to lists:
    LSHData.AppendThermoK(TempProbeT)
    LSHData.AppendThermoR(TempProbeR)
    LSHData.AppendControlR(ControlR)
    LSHData.AppendStressR(StressR)
    #Update CSV file
    LSHData.UpdateCSV()
    #Update Plot
    LSHData.UpdatePlot()
    ##Loop Back
    i = i + 1




print("===LakeShore Temperature Ramping Interface===")
print("o  Configuration Loaded.")
