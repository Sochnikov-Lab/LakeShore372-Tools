import serial
import io
from time import sleep
import numpy as np
#import pandas as pd
from datetime import datetime
from configparser import ConfigParser
import matplotlib.pyplot as plt

###LakeShore AC/Resistance Bridge Class###
class LakeShore372Device(object):
    #Initialization: create necessary variables and configurable serial instance
    def __init__(self):
        self.ID = ''         #ID of instrument
        self.ser = serial.Serial() #Serial Instance
        self.ser.timeout = 1 #read timeout --Should fix this to get rid of latency
        self.serIO = io.TextIOWrapper(io.BufferedRWPair(self.ser,self.ser),newline="\r\n")
        self.parser = ConfigParser()
    def getConfig(self,inifilename):
        self.parser.read(inifilename)
        self.serialcfg = {
            "serialport":str(self.parser.get('connection','serialport')),
            "baudrate":int(self.parser.get('connection','baudrate'))
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
            "autoscan":int(self.parser.get('scanner','autoscan')),
            "scannerpasses":int(self.parser.get('scanner','scannerpasses'))
        }
        #mixing chamber thermometer cfg
        self.mcthermo = {
            "channel":int(self.parser.get('mcthermometer','channel')),
            "curvenumber":int(self.parser.get('mcthermometer','curvenumber')),
            "tempcoeff":int(self.parser.get('mcthermometer','tempcoeff')),
            "filterwindow":int(self.parser.get('mcthermometer','filterwindow')),
            "t_dwell":float(self.parser.get('mcthermometer','t_dwell')),
            "t_pause":float(self.parser.get('mcthermometer','t_pause')),
            "t_settle":float(self.parser.get('mcthermometer','t_settle')),
            "excitemode":float(self.parser.get('mcthermometer','excitemode')),
            "excitesetting":float(self.parser.get('mcthermometer','excitesetting')),
            "autorange":float(self.parser.get('mcthermometer','autorange')),
            "range":float(self.parser.get('mcthermometer','range')),
            "units":float(self.parser.get('mcthermometer','units'))
        }
        self.sample1 = {
            "channel":int(self.parser.get('sample1','channel')),
            "curvenumber":int(self.parser.get('sample1','curvenumber')),
            "tempcoeff":int(self.parser.get('sample1','tempcoeff')),
            "filterwindow":int(self.parser.get('sample1','filterwindow')),
            "description":str(self.parser.get('sample1','description')),
            "t_dwell":float(self.parser.get('sample1','t_dwell')),
            "t_pause":float(self.parser.get('sample1','t_pause')),
            "t_settle":float(self.parser.get('sample1','t_settle')),
            "excitemode":float(self.parser.get('sample1','excitemode')),
            "excitesetting":float(self.parser.get('sample1','excitesetting')),
            "autorange":float(self.parser.get('sample1','autorange')),
            "range":float(self.parser.get('sample1','range')),
            "units":float(self.parser.get('sample1','units'))
        }
        self.sample2 = {
            "channel":int(self.parser.get('sample2','channel')),
            "curvenumber":int(self.parser.get('sample2','curvenumber')),
            "tempcoeff":int(self.parser.get('sample2','tempcoeff')),
            "filterwindow":int(self.parser.get('sample2','filterwindow')),
            "description":str(self.parser.get('sample2','description')),
            "t_dwell":float(self.parser.get('sample2','t_dwell')),
            "t_pause":float(self.parser.get('sample2','t_pause')),
            "t_settle":float(self.parser.get('sample2','t_settle')),
            "excitemode":float(self.parser.get('sample2','excitemode')),
            "excitesetting":float(self.parser.get('sample2','excitesetting')),
            "autorange":float(self.parser.get('sample2','autorange')),
            "range":float(self.parser.get('sample2','range')),
            "units":float(self.parser.get('sample2','units'))
        }
        #Timing
        self.timeConstants = {
            "t_therm":float(self.parser.get('timeconstants','t_therm')),
            "t_switch":float(self.parser.get('timeconstants','t_switch'))
        }
    #Attempts to open serial instance
    def open(self):
        try:
            self.ser.port = self.serialcfg["serialport"]
            self.ser.baudrate = self.serialcfg["baudrate"]
            self.ser.bytesize = serial.SEVENBITS
            self.ser.parity = serial.PARITY_ODD
            self.ser.stopbits = serial.STOPBITS_ONE
            self.ser.xonxoff = False #Turn off hardware flow control
            self.ser.rtscts = False #Turn off hardware RTS/CTS flow control
            self.ser.dsrdtr = False #Turn off hardware DSR/DTR flow control

            self.ser.open()


            #Read ID from Serial Port:
            #self.serIO.write(unicode('*IDN?\r'))
            self.serIO.flush()
            #self.ID = str(self.serIO.readline()).rstrip().lstrip()

            #Turn off all channels:
            for i in range(0,16):
                self.serIO.write(unicode('INSET' + str(i) + ',' + str(0) + ',' + str(0) + ',' + str(0) + ',' + str(0) + ',' + str(1) + '\r\n'))
                sleep(0.25)
        except serial.SerialException:
            print("**Failed to open serial port**")
    #Closes serial port
    def close(self):
        try:
            self.ser.close()
        except serial.SerialException:
            print("**Failed to close serial port**")
    def getDevID(self):
        self.serIO.write(unicode('*IDN?\r\n'))
        self.serIO.flush()
        return str(self.serIO.readline()).rstrip().lstrip()
    #Analog to INSET - Sets channel parameters / Enables channels
    def setCHParams(self,chdict,Enabled=1):
        self.serIO.write(unicode('INSET' + str(chdict["channel"]) + ',' + str(Enabled) + ',' + str(chdict["t_dwell"]) + ',' + str(chdict["t_pause"]) + ',' + str(chdict["curvenumber"]) + ',' + str(chdict["tempcoeff"]) + '\r\n'))
        self.serIO.flush()
    #Analog to INTYPE - Sets excitation settings, and turns on if Enabled = 1
    def Excite(self,chdict,Enabled=1):
        if Enabled == 1:
            currentShunt = 0
        else:
            currentShunt = 1
        self.serIO.write(unicode('INTYPE' + str(chdict["channel"]) + ',' + str(chdict["excitemode"]) + ',' + str(chdict["excitesetting"]) + ',' + str(chdict["autorange"]) + ',' + str(currentShunt) + ',' + str(chdict["units"]) + '\r\n'))
        self.serIO.flush()
    #Analog to FILTER - Sets filter if Enabled = 1.
    def setFilterParams(self,chdict,Enabled=1):
        self.serIO.write(unicode('FILTER' + str(chdict["channel"]) + ',' + str(Enabled) + ',' + str(chdict["t_settle"]) + ',' + str(chdict["filterwindow"]) + '\r\n'))
        self.serIO.flush()
    #Analog to RDGST? - Returns status for given channel
    def ReadCHStatus(self,chdict):
        self.serIO.write(unicode('RDGST?' + str(chdict["channel"]) + '\r\n'))
        self.serIO.flush()
        return str(self.serIO.readline()).rstrip().lstrip()
    #Analog to RDGR? - Returns resistance for given channel
    def ReadResistance(self,chdict):
        self.serIO.write(unicode('RDGR?' + str(chdict["channel"]) + '\r\n'))
        self.serIO.flush()
        return float(str(self.serIO.readline()).rstrip().lstrip())
    #Analog to RDGK? - Returns kelvin temperature for given channel
    def ReadKelvin(self,chdict):
        self.serIO.write(unicode('RDGK?' + str(chdict["channel"]) + '\r\n'))
        self.serIO.flush()
        return float(self.serIO.readline())
        #return float(str(self.serIO.readline()).rstrip().lstrip())
    def ScanTo(self,chdict,AUTOSCAN=0):
        self.serIO.write(unicode('SCAN' + str(chdict["channel"]) + ',' + str(AUTOSCAN) + '\r\n'))
        self.serIO.flush()
        #return float(str(self.serIO.readline()).rstrip().lstrip())
    def HeaterOn(self):
        self.serIO.write(unicode('OUTMODE0,2,16,0,0,5\r\n'))
        self.serIO.flush()
    def HeaterOff(self):
        self.serIO.write(unicode('OUTMODE0,0,16,0,0,5\r\n'))
        self.serIO.flush()
    def SetSampleHeaterCurrent(self,htrdict):
        self.serIO.write(unicode('HTRSET0,' + str(htrdict["resistance"]) + ',0,' + str(htrdict["maxcurrent"]) + ',' + str(htrdict["disp"]) + '\r\n'))
        self.serIO.flush()
        #return float(str(self.serIO.readline()).rstrip().lstrip())
    def SetSampleHeaterRange(self,htrdict):
        self.serIO.write(unicode('RANGE0,' + str(htrdict["range"]) + '\r\n'))
        self.serIO.flush()
    def SetSampleHeaterOut(self,htrpc):
        self.serIO.write(unicode('MOUT,' + str(htrpc) + '\r\n'))
        self.serIO.flush()

#Data Handler Class (Saves/Plots data)
class LakeShore372Data(object):
    def __init__(self,DataFile):
        #Lists of timestamps / Heater percents / Resistances / Temperatures
        self.timestamp = []
        self.htrpc = []
        self.MCThermoR = []
        self.MCThermoK = []
        self.Sample1R = []
        self.Sample2R = []
        #Last Read Value:
        self.timesamp = ""
        self.htrpcL = 0.0
        self.MCThermoRL = 0.0
        self.MCThermoKL = 0.0
        self.Sample1RL = 0.0
        self.Sample2RL = 0.0
        #CSV file
        self.DataFile = DataFile
        #plot
        self.pltfig = plt.figure()
        self.ax = plt.gca()
        plt.ion() #Interactive Plotting
        self.LegendApplied = False
        #Write Header:
        self.DataFile.write("time,heater%,MCTemp,MCResist,1Resistance,2Resistance\n")

    def AppendMCThermoR(self,RReading):
        self.MCThermoRL = RReading
        self.MCThermoR.append(RReading)
    def AppendMCThermoK(self,KReading):
        self.MCThermoRK = KReading
        self.MCThermoK.append(KReading)
    def AppendSample1R(self,RReading):
        self.Sample1RL = RReading
        self.Sample1R.append(RReading)
    def AppendSample2R(self,RReading):
        self.Sample2RL = RReading
        self.Sample2R.append(RReading)
    def UpdateCSV(self,htrpc):
        self.DataFile.write(str(datetime.now().strftime('%Y%m%d%H%M%S')) + ',' + str(htrpc) + ',' + str(self.MCThermoKL) + ',' +str(self.MCThermoRL) + ',' +str(self.Sample1RL) + ',' +str(self.Sample2RL) + '\n')
    def UpdatePlot(self,sample1desc,sample2desc):
        s1plt = self.ax.scatter(self.MCThermoK,self.Sample1R,c='b',label=sample1desc)
        s2plt = self.ax.scatter(self.MCThermoK,self.Sample2R,c='r',label=sample2desc)
        self.ax.set_title("Resistances vs. Temperature")
        self.ax.set_xlabel("Temperature [K]")
        self.ax.set_ylabel("Resistance [$\Omega$]")
        if self.LegendApplied == False:
            self.ax.legend()
            self.LegendApplied = True

        plt.pause(0.05)
        print("Plot Updated")
