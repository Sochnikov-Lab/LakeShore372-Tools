#Run this file using >python InterpolateCSV.py [Inputfilename.csv].
#Output will be in a file "Inputfilename_interp.csv"

import sys
import os
import numpy as np
import pandas as pd
from configparser import ConfigParser
import matplotlib.pyplot as plt

#Get Header Names from ini file:
cfgparser = ConfigParser()
cfgparser.read("config.ini")
nChannels = int(cfgparser.get('scanner','channels')) #Number of channels holding samples

#CSV header names:
datehdr = "date"
timehdr = "time"
htrhdr = "heater%"
MCThdr = "MCTemp"
MCRhdr = "MCResist"
s1hdr = str(cfgparser.get('sample1','description')).strip('\"') #Sample 1 Header
s2hdr = str(cfgparser.get('sample2','description')).strip('\"') #Sample 2 Header
s3hdr = str(cfgparser.get('sample3','description')).strip('\"') #Sample 3 Header

#Read in CSV file as lists:
argfilename = str(sys.argv[1])
dataframe = pd.read_csv(argfilename)

DateList = dataframe[datehdr] #List of dates
TimeList = dataframe[timehdr] #list of times
htrList = dataframe[htrhdr] #List of heater percents
MCTList = dataframe[MCThdr] #List of MC temperatures
MCRList = dataframe[MCRhdr] #List of MC resistances
s1List = dataframe[s1hdr] #List of resistances for Sample 1
s2List = dataframe[s2hdr] #List of resistances for Sample 2
s3List = dataframe[s3hdr] #List of resistances for Sample 3

#Do interpolation according to: (Item[i] + item[i+1]) / 2
Interp_MCTList = [] #List of interpolated temperatures
length = len(MCTList)-1
for i in range(0,length):
    Interp_MCTList.append((MCTList[i] + MCTList[i+1]) / 2.0)

#Open a new csv file, appending _interp to input filename:
outputfilename = os.path.splitext(argfilename)[0] + "_interp.csv"
interpcsv = open(outputfilename,'w')

#Write header:
interpcsv.write(datehdr + ',' + timehdr + ',' + htrhdr + ',' + MCThdr + ',' + MCThdr + '_Interp'  + ',' + MCRhdr + ',' +s1hdr + ',' + s2hdr + ',' + s3hdr + '\n')
#Write interpolated values and existing values to new CSV
for i in range(0,length):
    interpcsv.write(str(DateList[i]) + ',' + str(TimeList[i]) + ',' + str(htrList[i]) + ',' + str(MCTList[i]) + ',' + str(Interp_MCTList[i]) + ',' +str(MCRList[i]) + ',' +str(s1List[i]) + ',' +str(s2List[i]) + ',' + str(s3List[i]) + '\n')

#close the file:
interpcsv.close()
