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
        self.ser = serial.Serial() #Serial Instance
        self.ser.timeout = 0.25 #read timeout --Should fix this to get rid of latency
        self.serIO = io.TextIOWrapper(io.BufferedRWPair(self.ser,self.ser),newline='\r\n')
    #Attempts to open serial instance
    def open(self,COMPORT,BAUDRATE=115200):
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
        self.MCThermoR = []
        self.MCThermoK = []
        self.Sample1R = []
        self.Sample2R = []
        #Last Read Value:
        self.MCThermoRL = 0.0
        self.MCThermoKL = 0.0
        self.Sample1RL = 0.0
        self.Sample2RL = 0.0
        #CSV file
        self.DataFile = DataFile
        #Write Header:
        self.DataFile.write("MCTemp,MCResist,1Resistance,2Resistance\n")



    def AppendMCThermoR(self,RReading):
        self.MCThermoRL = RReading
        self.MCThermoR.append(RReading)
    def AppendMCThermoK(self,KReading):
        self.MCThermoRK = RReading
        self.MCThermoK.append(KReading)
    def AppendSample1R(self,RReading):
        self.Sample1RL = RReading
        self.Sample1R.append(RReading)
    def AppendSample2R(self,RReading):
        self.Sample2RL = RReading
        self.Sample2R.append(RReading)
    def UpdateCSV(self):
        self.DataFile.write(str(self.MCThermoKL) + ',' +str(self.MCThermoRL) + ',' +str(self.Sample1RL) + ',' +str(self.Sample2RL) + '\n')
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
sampleHeater = {
    "resistance":float(cfgparser.get('sampleheater','resistance')),
    "maxcurrent":float(cfgparser.get('sampleheater','maxcurrent')),
    "range":float(cfgparser.get('sampleheater','range')),
    "disp":int(cfgparser.get('sampleheater','disp')),
    "initpc":float(cfgparser.get('sampleheater','initpc'))/100.0,
    "finalpc":float(cfgparser.get('sampleheater','finalpc'))/100.0,
    "deltapc":float(cfgparser.get('sampleheater','deltapc'))/100.0
}
#Scanner Configuration
scannerChannelMap = {
    "mcthermometer":int(cfgparser.get('scannerch','mcthermometer')),
    "sample1":int(cfgparser.get('scannerch','sample1')),
    "sample2":int(cfgparser.get('scannerch','sample2')),
    "autoscan":int(cfgparser.get('scannerch','autoscan'))
}
#Timing
timeConstants = {
    "t_therm":float(cfgparser.get('timeconstants','t_const')),
    "t_switch":float(cfgparser.get('timeconstants','t_switch')),
    "t_dwell":float(cfgparser.get('timeconstants','t_dwell')),
    "t_settle":float(cfgparser.get('timeconstants','t_settle'))
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
LSH.SetSampleHeaterRange(sampleHeater["range"])


##Main Loop:
i = 0 #step number

while currentpc < sampleHeater["finalpc"]:
    #Set Current
    currentpc = sampleHeater["initpc"] + ((i)**(1.0/2.0)) * sampleHeater["stepsizepc"]
    #Wait Thermalization
    sleep(timeConstants["t_therm"])
    #Wait (Other)
    LSH.ScanTo(scannerChannelMap["mcthermometer"],scannerChannelMap["autoscan"])
    sleep(timeConstants["t_switch"] + timeConstants["t_settle"])
    #Scan to Temp Probe, Read Temp Probe T/R
    TempProbeT = LSH.ReadKelvin(scannerChannelMap["mcthermometer"])
    sleep(1.0)
    TempProbeR = LSH.ReadResistance(scannerChannelMap["mcthermometer"])
    #Wait (Other)
    LSH.ScanTo(scannerChannelMap["Sample1"],scannerChannelMap["autoscan"])
    sleep(timeConstants["t_switch"] + timeConstants["t_settle"])
    #Scan to Sample1 Sample, Read R
    Sample1R = LSH.ReadResistance(scannerChannelMap["Sample1"])
    #Wait (Other)
    LSH.ScanTo(scannerChannelMap["Sample2"],scannerChannelMap["autoscan"])
    sleep(timeConstants["t_switch"] + timeConstants["t_settle"])
    #Scan to Sample2ed Sample, Read R
    Sample2R = LSH.ReadResistance(scannerChannelMap["Sample2"])
    #Append values to lists:
    LSHData.AppendMCThermoK(TempProbeT)
    LSHData.AppendMCThermoR(TempProbeR)
    LSHData.AppendSample1R(Sample1R)
    LSHData.AppendSample2R(Sample2R)
    #Update CSV file
    LSHData.UpdateCSV()
    #Update Plot
    LSHData.UpdatePlot()
    ##Loop Back
    i = i + 1




print("===LakeShore Temperature Ramping Interface===")
print("o  Configuration Loaded.")
