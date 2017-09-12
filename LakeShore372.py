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
            "initpc":float(self.parser.get('sampleheater','initpc')),
            "finalpc":float(self.parser.get('sampleheater','finalpc')),
            "deltapc":float(self.parser.get('sampleheater','deltapc'))
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
            "excitemode":int(self.parser.get('mcthermometer','excitemode')),
            "excitesetting":int(self.parser.get('mcthermometer','excitesetting')),
            "autorange":int(self.parser.get('mcthermometer','autorange')),
            "range":int(self.parser.get('mcthermometer','range')),
            "units":int(self.parser.get('mcthermometer','units'))
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
            "excitemode":int(self.parser.get('sample1','excitemode')),
            "excitesetting":int(self.parser.get('sample1','excitesetting')),
            "autorange":int(self.parser.get('sample1','autorange')),
            "range":int(self.parser.get('sample1','range')),
            "units":int(self.parser.get('sample1','units'))
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
            "excitemode":int(self.parser.get('sample2','excitemode')),
            "excitesetting":int(self.parser.get('sample2','excitesetting')),
            "autorange":int(self.parser.get('sample2','autorange')),
            "range":int(self.parser.get('sample2','range')),
            "units":int(self.parser.get('sample2','units'))
        }
        self.sample3 = {
            "channel":int(self.parser.get('sample3','channel')),
            "curvenumber":int(self.parser.get('sample3','curvenumber')),
            "tempcoeff":int(self.parser.get('sample3','tempcoeff')),
            "filterwindow":int(self.parser.get('sample3','filterwindow')),
            "description":str(self.parser.get('sample3','description')),
            "t_dwell":float(self.parser.get('sample3','t_dwell')),
            "t_pause":float(self.parser.get('sample3','t_pause')),
            "t_settle":float(self.parser.get('sample3','t_settle')),
            "excitemode":int(self.parser.get('sample3','excitemode')),
            "excitesetting":int(self.parser.get('sample3','excitesetting')),
            "autorange":int(self.parser.get('sample3','autorange')),
            "range":int(self.parser.get('sample3','range')),
            "units":int(self.parser.get('sample3','units'))
        }
        #Timing
        self.timeConstants = {
            "t_therm":float(self.parser.get('timeconstants','t_therm')),
            "t_switch":float(self.parser.get('timeconstants','t_switch')),
            "t_maxARsleep":float(self.parser.get('timeconstants','t_maxARsleep'))
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
            sleep(.05)


            #Read ID from Serial Port:
            #self.serIO.write(unicode('*IDN?\r'))
            self.serIO.flush()
            #self.ID = str(self.serIO.readline()).rstrip().lstrip()

            #Turn off all channels:
            #for i in range(0,16):
            #    self.serIO.write(unicode('INSET' + str(i) + ',' + str(0) + ',' + str(0) + ',' + str(0) + ',' + str(0) + ',' + str(1) + '\r\n'))
            #    sleep(0.25)
        except serial.SerialException:
            print("**Failed to open serial port**")
    #Closes serial port
    def close(self):
        try:
            self.ser.close()
        except serial.SerialException:
            print("**Failed to close serial port**")
    def getDevID(self):
        sleep(0.1)
        self.serIO.write(unicode('*IDN?\r\n'))
        sleep(0.1)
        self.serIO.flush()
        slppe(0.05)
        return str(self.serIO.readline()).rstrip().lstrip()
    #Analog to INSET - Sets channel parameters / Enables channels
    def setCHParams(self,chdict,Enabled=1):
        sleep(0.05)
        self.serIO.write(unicode('INSET' + str(chdict["channel"]) + ',' + str(1) + ',' + str(chdict["t_dwell"]) + ',' + str(chdict["t_pause"]) + ',' + str(chdict["curvenumber"]) + ',' + str(chdict["tempcoeff"]) + '\r\n'))
        sleep(0.05)
        self.serIO.flush()
        sleep(0.05)
    #Analog to INTYPE - Sets excitation settings, and turns on if Enabled = 1
    def Excite(self,chdict):
        sleep(0.05)
        self.serIO.write(unicode('INTYPE' + str(chdict["channel"]) + ',' + str(chdict["excitemode"]) + ',' + str(chdict["excitesetting"]) + ',' + str(chdict["autorange"]) + ',' + str(chdict["range"]) + ',' + str(0) + ',' + str(chdict["units"]) + '\r\n'))
        sleep(0.05)
        self.serIO.flush()
    def ExciteOff(self,chdict):
        sleep(0.05)
        self.serIO.write(unicode('INTYPE' + str(chdict["channel"]) + ',' + str(chdict["excitemode"]) + ',' + str(chdict["excitesetting"]) + ',' + str(chdict["autorange"]) + ',' + str(chdict["range"]) + ',' + str(1) + ',' + str(chdict["units"]) + '\r\n'))
        sleep(0.05)
        self.serIO.flush()
    #Analog to FILTER - Sets filter if Enabled = 1.
    def setFilterParams(self,chdict,Enabled=1):
        sleep(0.05)
        self.serIO.write(unicode('FILTER' + str(chdict["channel"]) + ',' + str(Enabled) + ',' + str(chdict["t_settle"]) + ',' + str(chdict["filterwindow"]) + '\r\n'))
        sleep(0.05)
        self.serIO.flush()
    #Analog to RDGST? - Returns status for given channel
    def ReadCHStatus(self,chdict):
        sleep(.1)
        self.serIO.write(unicode('RDGST?' + str(chdict["channel"]) + '\r\n'))
        sleep(0.1)
        self.serIO.flush()
        sleep(0.1)
        return str(self.serIO.readline()).rstrip().lstrip()
    #Analog to RDGR? - Returns resistance for given channel
    def ReadResistance(self,chdict):
        sleep(0.1)
        self.serIO.write(unicode('RDGR?' + str(chdict["channel"]) + '\r\n'))
        sleep(0.1)
        self.serIO.flush()
        sleep(0.1)
        return float(str(self.serIO.readline()).rstrip().lstrip())
    #Analog to RDGK? - Returns kelvin temperature for given channel
    def ReadKelvin(self,chdict):
        sleep(0.1)
        self.serIO.write(unicode('RDGK?' + str(chdict["channel"]) + '\r\n'))
        sleep(0.1)
        self.serIO.flush()
        return float(self.serIO.readline())
        #return float(str(self.serIO.readline()).rstrip().lstrip())
    def ScanTo(self,chdict,AUTOSCAN=0):
        sleep(0.1)
        self.serIO.write(unicode('SCAN' + str(chdict["channel"]) + ',' + str(AUTOSCAN) + '\r\n'))
        sleep(0.1)
        self.serIO.flush()
        #return float(str(self.serIO.readline()).rstrip().lstrip())
    def HeaterOn(self):
        sleep(0.1)
        self.serIO.write(unicode('OUTMODE0,2,16,0,0,5\r\n'))
        sleep(0.1)
        self.serIO.flush()
    def HeaterOff(self):
        sleep(0.1)
        self.serIO.write(unicode('OUTMODE0,0,16,0,0,5\r\n'))
        sleep(0.1)
        self.serIO.flush()
    def SetSampleHeaterCurrent(self,htrdict):
        sleep(0.1)
        self.serIO.write(unicode('HTRSET0,' + str(htrdict["resistance"]) + ',0,' + str(htrdict["maxcurrent"]) + ',' + str(htrdict["disp"]) + '\r\n'))
        sleep(0.1)
        self.serIO.flush()
        sleep(0.1)
        #return float(str(self.serIO.readline()).rstrip().lstrip())
    def SetSampleHeaterRange(self,htrdict):
        sleep(0.1)
        self.serIO.write(unicode('RANGE0,' + str(htrdict["range"]) + '\r\n'))
        sleep(0.1)
        self.serIO.flush()
        sleep(0.1)
    def SetSampleHeaterOut(self,htrpc):
        sleep(0.1)
        self.serIO.flush()
        sleep(0.1)
        self.serIO.write(unicode('MOUT0, ' + "{:.2f}".format(htrpc) + '\r\n'))
        sleep(.1)
        self.serIO.flush()
        #str(self.serIO.readline())
        sleep(.1)
        self.serIO.flush()
        sleep(0.1)
    def ReadSampleHeater(self):
        sleep(0.1)
        self.serIO.flush()
        sleep(0.1)
        self.serIO.write(unicode('MOUT? 0' + '\r\n'))
        sleep(.1)
        self.serIO.flush()
        return str(self.serIO.readline())


#Data Handler Class (Saves/Plots data)
class LakeShore372Data(object):
    def __init__(self,DataFile,sample1desc,sample2desc,sample3desc):
        #Lists of timestamps / Heater percents / Resistances / Temperatures
        self.timestamp = []
        self.htrpc = []
        self.MCThermoR = []
        self.MCThermoK = []
        self.Sample1R = []
        self.Sample2R = []
        self.Sample3R = []
        #Last Read Value:
        self.timesamp = ""
        self.htrpcL = 0.0
        self.MCThermoRL = 0.0
        self.MCThermoKL = 0.0
        self.Sample1RL = 0.0
        self.Sample2RL = 0.0
        self.Sample3RL = 0.0
        #CSV file
        self.DataFile = DataFile
        self.DataFileName = DataFile.name
        #plot
        self.pltfig = plt.figure()
        plt.grid() #Turns on gridlines
        self.ax = plt.gca()
        plt.ion() #Interactive Plotting
        self.LegendApplied = False
        #Write Header:
        self.DataFile.write("date,time,heater%,MCTemp,MCResist,"+sample1desc+","+ sample2desc+","+ sample3desc+"\n")

    def AppendMCThermoR(self,RReading):
        self.MCThermoRL = RReading
        self.MCThermoR.append(RReading)
    def AppendMCThermoK(self,KReading):
        self.MCThermoKL = KReading
        self.MCThermoK.append(KReading)
    def AppendSample1R(self,RReading):
        self.Sample1RL = RReading
        self.Sample1R.append(RReading)
    def AppendSample2R(self,RReading):
        self.Sample2RL = RReading
        self.Sample2R.append(RReading)
    def AppendSample3R(self,RReading):
        self.Sample3RL = RReading
        self.Sample3R.append(RReading)
    def UpdateCSV(self,htrpc):
        success = False
        attempts = 0
        print("o  Attempting to Save CSV")
        while success == False and attempts < 3:
            try:
                if self.DataFile.closed == True:
                    self.DataFile = open(self.DataFileName,'a')
                self.DataFile.write(str(datetime.now().strftime('%Y/%m/%d')) + ',' + str(datetime.now().strftime('%H:%M:%S')) + ',' + str(htrpc) + ',' + str(self.MCThermoKL) + ',' +str(self.MCThermoRL) + ',' +str(self.Sample1RL) + ',' +str(self.Sample2RL) + ',' + str(self.Sample3RL) + '\n')
                self.DataFile.close() #Close to prevent errors to be proactive about corruption
                print("o  Saved CSV")
                success = True
            except IOError:
                sleep(10)
                print("**FileIO Error. Is the file currently open in another application? (Attempt " + str(attempts+1) + " of 3)**")
                attempts += 1
    def UpdateCSV_S1(self,htrpc):
        success = False
        attempts = 0
        print("o  Attempting to Save CSV")
        while success == False and attempts < 3:
            try:
                if self.DataFile.closed == True:
                    self.DataFile = open(self.DataFileName,'a')
                self.DataFile.write(str(datetime.now().strftime('%Y/%m/%d')) + ',' + str(datetime.now().strftime('%H:%M:%S')) + ',' + str(htrpc) + ',' + str(self.MCThermoKL) + ',' +str(self.MCThermoRL) + ',' +str(self.Sample1RL) + ',' + '' + ',' + '' + '\n')
                self.DataFile.close() #Close to prevent errors to be proactive about corruption
                print("o  Saved CSV")
                success = True
            except IOError:
                sleep(10)
                print("**FileIO Error. Is the file currently open in another application? (Attempt " + str(attempts+1) + " of 3)**")
                attempts += 1
    def UpdateCSV_S2(self,htrpc):
        success = False
        attempts = 0
        print("o  Attempting to Save CSV")
        while success == False and attempts < 3:
            try:
                if self.DataFile.closed == True:
                    self.DataFile = open(self.DataFileName,'a')
                self.DataFile.write(str(datetime.now().strftime('%Y/%m/%d')) + ',' + str(datetime.now().strftime('%H:%M:%S')) + ',' + str(htrpc) + ',' + str(self.MCThermoKL) + ',' +str(self.MCThermoRL) + ',' + '' + ',' +str(self.Sample2RL) + ',' + '' + '\n')
                self.DataFile.close() #Close to prevent errors to be proactive about corruption
                print("o  Saved CSV")
                success = True
            except IOError:
                sleep(10)
                print("**FileIO Error. Is the file currently open in another application? (Attempt " + str(attempts+1) + " of 3)**")
                attempts += 1
    def UpdateCSV_S3(self,htrpc):
        success = False
        attempts = 0
        print("o  Attempting to Save CSV")
        while success == False and attempts < 3:
            try:
                if self.DataFile.closed == True:
                    self.DataFile = open(self.DataFileName,'a')
                self.DataFile.write(str(datetime.now().strftime('%Y/%m/%d')) + ',' + str(datetime.now().strftime('%H:%M:%S')) + ',' + str(htrpc) + ',' + str(self.MCThermoKL) + ',' +str(self.MCThermoRL) + ',' + '' + ',' + '' + ',' + str(self.Sample3RL) + '\n')
                self.DataFile.close() #Close to prevent errors to be proactive about corruption
                print("o  Saved CSV")
                success = True
            except IOError:
                sleep(10)
                print("**FileIO Error. Is the file currently open in another application? (Attempt " + str(attempts+1) + " of 3)**")
                attempts += 1


    def UpdatePlot(self,sample1desc,sample2desc,sample3desc):
        plt.cla()
        s1plt = self.ax.scatter(self.MCThermoK,self.Sample1R,c='k',s=5,label=sample1desc)
        s2plt = self.ax.scatter(self.MCThermoK,self.Sample2R,c='r',s=5,label=sample2desc)
        s3plt = self.ax.scatter(self.MCThermoK,self.Sample3R,c='b',s=5,label=sample3desc)
        self.ax.set_title("Resistances vs. Temperature")
        self.ax.set_xlabel("Temperature [K]")
        self.ax.set_ylabel("Resistance [$\Omega$]")
        self.ax.legend()

        plt.pause(0.05)
        print("Plot Updated")
