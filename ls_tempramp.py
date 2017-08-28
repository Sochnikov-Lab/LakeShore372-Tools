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
        self.parser = ConfigParser()

    def getConfig(self,inifilename)
        self.parser.read('config.ini')
        self.serialcfg = {
            "port":str(self.parser.get('connection','serialport')),
            "baud":int(self.parser.get('connection','baudrate'))
        }
        #sample heater configuration
        #resistance: Ohms
        #maxCurrent: A
        self.sampleheater = {
            "resistance":float(self.parser.get('sampleheater','resistance')),
            "maxcurrent":float(self.parser.get('sampleheater','maxcurrent')),
            "range":float(self.parser.get('sampleheater','range')),
            "disp":int(self.parser.get('sampleheater','disp')),
            "initpc":float(self.parser.get('sampleheater','initpc'))/100.0,
            "finalpc":float(self.parser.get('sampleheater','finalpc'))/100.0,
            "deltapc":float(self.parser.get('sampleheater','deltapc'))/100.0
        }
        #Scanner cfg
        self.scanner = {
            "mcthermometer":int(self.parser.get('scannerch','mcthermometer')),
            "sample1":int(self.parser.get('scannerch','sample1')),
            "sample2":int(self.parser.get('scannerch','sample2')),
            "autoscan":int(self.parser.get('scannerch','autoscan'))
        }
        #mixing chamber thermometer cfg
        self.mcthermo = {
            "channel":int(self.parser.get('mcthermometer','channel')),
            "curvenumber":int(self.parser.get('mcthermometer','curvenumber')),
            "tempcoeff":int(self.parser.get('mcthermometer','tempcoeff')),
            "filterwindow":int(self.parser.get('mcthermometer','filterwindow'))
            "t_dwell":float(self.parser.get('mcthermometer','t_dwell')),
            "t_pause":float(self.parser.get('mcthermometer','t_pause')),
            "t_settle":float(self.parser.get('mcthermometer','t_settle'))
        }
        self.sample1 = {
            "channel":int(self.parser.get('sample1','channel')),
            "curvenumber":int(self.parser.get('sample1','curvenumber')),
            "tempcoeff":int(self.parser.get('sample1','tempcoeff')),
            "filterwindow":int(self.parser.get('sample1','filterwindow')),
            "description":str(self.parser.get('sample1','description'))
            "t_dwell":float(self.parser.get('sample1','t_dwell')),
            "t_pause":float(self.parser.get('sample1','t_pause')),
            "t_settle":float(self.parser.get('sample1','t_settle'))
        }
        self.sample2 = {
            "channel":int(self.parser.get('sample2','channel')),
            "curvenumber":int(self.parser.get('sample2','curvenumber')),
            "tempcoeff":int(self.parser.get('sample2','tempcoeff')),
            "filterwindow":int(self.parser.get('sample2','filterwindow')),
            "description":str(self.parser.get('sample2','description'))
            "t_dwell":float(self.parser.get('sample2','t_dwell')),
            "t_pause":float(self.parser.get('sample2','t_pause')),
            "t_settle":float(self.parser.get('sample2','t_settle'))
        }
        #Timing
        self.timeConstants = {
            "t_therm":float(self.parser.get('timeconstants','t_const')),
            "t_switch":float(self.parser.get('timeconstants','t_switch'))
        }
    #Attempts to open serial instance
    def open(self):
        try:
            self.ser.port = self.serialcfg["serialport"]
            self.ser.baudrate = self.serialcfg["baudrate"]
            self.ser.open()
            #Read ID from Serial Port:
            self.serIO.write(unicode('*IDN?\r'))
            self.serIO.flush()
            self.ID = str(self.serIO.readline()).rstrip().lstrip()

            #Turn off all channels:
            for i in range(0,16):
                self.serIO.write(unicode('INSET' + str(CH) + ',' + str(0) + ',' + str(0) + ',' + str(0) + ',' + str(0) + ',' + str(1) + '\r'))
                sleep(0.125)
        except serial.SerialException:
            print("**Failed to open serial port**")
    def close(self,verbose=0):
        try:
            self.ser.close()
        except serial.SerialException:
            print("**Failed to close serial port**")
    def setCHParams(self,chdict,Enabled=1):
        self.serIO.write(unicode('INSET' + str(chdict["channel"]) + ',' + str(Enabled) + ',' + str(chdict["t_dwell"]) + ',' + str(chdict["t_pause"]) + ',' + str(chdict["curvenumber"]) + ',' + str(chdict["tempcoeff"]) + '\r'))
        self.serIO.flush()
    def setFilterParams(self,chdict,Enabled=1):
        self.serIO.write(unicode('FILTER' + str(chdict[channel]) + ',' + str(Enabled) + ',' + str(chdict["t_settle"]) + ',' + str(chdict["filterwindow"]) + '\r'))
        self.serIO.flush()
    def ReadCHStatus(self,chdict):
        self.serIO.write(unicode('RDGST?' + str(chdict["channel"]) + '\r'))
        self.serIO.flush()
        return str(self.serIO.readline()).rstrip().lstrip()
    def ReadResistance(self,chdict):
        self.serIO.write(unicode('RDGR?' + str(chdict["channel"]) + '\r'))
        self.serIO.flush()
        return float(str(self.serIO.readline()).rstrip().lstrip())
    def ReadKelvin(self,chdict):
        self.serIO.write(unicode('RDGK?' + str(chdict["channel"]) + '\r'))
        self.serIO.flush()
        return float(str(self.serIO.readline()).rstrip().lstrip())
    def ScanTo(self,chdict,AUTOSCAN=0):
        self.serIO.write(unicode('SCAN' + str(chdict["channel"]) + ',' + str(AUTOSCAN) + '\r'))
        self.serIO.flush()
        #return float(str(self.serIO.readline()).rstrip().lstrip())
    def SetSampleHeaterCurrent(self,htrdict):
        self.serIO.write(unicode('HTRSET0,' + str(htrdict["resistance"]) + ',0,' + str(htrdict["maxcurrent"]) + ',' + str(htrdict["disp"]) + '\r'))
        self.serIO.flush()
        #return float(str(self.serIO.readline()).rstrip().lstrip())
    def SetSampleHeaterRange(self,htrdict):
        self.serIO.write(unicode('RANGE0,' + str(htrdict["range"]) + '\r'))
        self.serIO.flush()
class LakeShoreConfig(object):
    def __init__(self,configfilename):
        self.parser = ConfigParser()

#Data Handler Class (Saves/Plots data)
class LakeShore372Data(object):
    def __init__(self,DataFile):
        #Lists of timestamps / Heater percents / Resistances / Temperatures
        self.htrpc = []
        self.MCThermoR = []
        self.MCThermoK = []
        self.Sample1R = []
        self.Sample2R = []
        #Last Read Value:
        self.htrpcL = 0.0
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
LSHCfg = LakeShoreConfig('config.ini')
#Connection configuration


#First, create and open instance of the LakeShore372 class:
LSHDev = LakeShore372()
LSHDev.open(LSHCfg.serial)
#Second, Create Instance of the data handler class and a datafile:
FileDescription = raw_input("What should we call the file? ")
DateStr = datetime.now().strftime('%Y%m%d%-H%M%S')
DataFileName = DateStr + '_' + FileDescription + '.csv'
LSHDataFile = open(DataFileName,'w')
LSHData = LakeShore372Data(LSHDataFile)

#next, send one-time configuration over serial:
#heater:
LSHDev.SetSampleHeaterRange(sampleHeater)
#thermometer:
LSHDev.setCHParams(mcthermo,1)
LSHDev.setFilterParams(mcthermo)
#sample1:
LSHDev.setCHParams(sample1,1)
LSHDev.setFilterParams(sample1)
#sample2:
LSHDev.setCHParams(sample2,1)
LSHDev.setFilterParams(sample2)



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
