import serial
import io
import time
import numpy as np
import pandas as pd
from datetime import datetime
from configparser import ConfigParser
import LakeShore372 as ls

###Script###
#Open up a serial connection after loading config file:
LSHDev = ls.LakeShore372Device() #Create and open instance of the LakeShore372 class
LSHDev.getConfig('config.ini') #Load configuration/ini file
LSHDev.open() #Open serial port designated in ini file.



#Open a file to write to, with a description given by the user at runtime.
FileDescription = raw_input("What should we call the file? ")#Get user description for this run
DataFileName = datetime.now().strftime('%Y%m%d%-H%M%S') + '_' + FileDescription + '.csv' #give it a dated filename
LSHDataFile = open(DataFileName,'w') #Open the file
LSHData = ls.LakeShore372Data(LSHDataFile) #Pass file to data handler class

#next, send one-time configuration over serial:
#heater:
LSHDev.SetSampleHeaterRange(LSHDev.sampleHeater)
#thermometer:
LSHDev.setCHParams(LSHDev.mcthermo,1) #Set the MC thermometer channel preferences
LSHDev.setFilterParams(LSHDev.mcthermo) #Set the filter prefs for the MC thermometer
LSHDev.Excite(LSHDev.mcthermo) #Sets excitation parameters for MC thermometer
#sample1:
LSHDev.setCHParams(LSHDev.sample1,1)
LSHDev.setFilterParams(LSHDev.sample1)
LSHDev.Excite(LSHDev.sample1) #Sets excitation parameters for MC thermometer
#sample2:
LSHDev.setCHParams(LSHDev.sample2,1)
LSHDev.setFilterParams(LSHDev.sample2)
LSHDev.Excite(LSHDev.sample2) #Sets excitation parameters for MC thermometer



##Main Loop:
i = 0 #step number

while currentpc < LSHDev.sampleHeater["finalpc"]:
    #Set Current
    currentpc = LSHDev.sampleHeater["initpc"] + ((i)**(1.0/2.0)) * LSHDev.sampleHeater["stepsizepc"]
    #Wait Thermalization
    sleep(LSHDev.timeConstants["t_therm"])

    for measurement in range(0,LSHDev.scanner["scannerpasses"]):
        #Wait (Other)
        LSH.ScanTo(LSHDev.mcthermometer)
        sleep(LSHDev.timeConstants["t_switch"] + LSHDev.mcthermometer["t_settle"])
        #Scan to Temp Probe, Read Temp Probe T/R
        TempProbeT = LSH.ReadKelvin(LSHDev.mcthermometer)
        sleep(1.0)
        TempProbeR = LSH.ReadResistance(LSHDev.mcthermometer)
        LSHData.AppendMCThermoK(TempProbeT)
        LSHData.AppendMCThermoR(TempProbeR)

        #Wait (Other)
        LSH.ScanTo(LSHDev.sample1)
        sleep(LSHDev.timeConstants["t_switch"] + LSHDev.sample1["t_settle"])
        #Scan to Sample1 Sample, Read R
        Sample1R = LSH.ReadResistance(LSHDev.sample1)
        LSHData.AppendSample1R(Sample1R)
        #Wait (Other)
        LSH.ScanTo(LSHDev.sample2)
        sleep(LSHDev.timeConstants["t_switch"] + LSHDev.sample2["t_settle"])
        #Scan to Sample2ed Sample, Read R
        Sample2R = LSH.ReadResistance(LSHDev.sample2)
        LSHData.AppendSample2R(Sample2R)
        #Update CSV file
        LSHData.UpdateCSV(currentpc)
        #Update Plot
        LSHData.UpdatePlot()
    ##Loop Back
    i = i + 1
