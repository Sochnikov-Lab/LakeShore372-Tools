#This tosses out the 4th sample 3 measurement of each heater value. (Due to badly implemented interpolation)
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
MCTInterphdr = MCThdr + "_Interp"
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
MCTInterpList = dataframe[MCTInterphdr]
MCRList = dataframe[MCRhdr] #List of MC resistances
s1List = dataframe[s1hdr] #List of resistances for Sample 1
s2List = dataframe[s2hdr] #List of resistances for Sample 2
s3List = dataframe[s3hdr] #List of resistances for Sample 3

#Adjust lists to not include NaN:
MCTInterpListS1 = []
MCTInterpListS2 = []
MCTInterpListS3 = []
s1ListADJ = []
s2ListADJ = []
s3ListADJ = []

#4th measurement is interpolated badly.
#4th measurement (i) of each heater val highlighted: 0 1 2 *3* 4 5 6 *7* 8 9 10 *11*
#                            (i+1)                   1 2 3 *4* 5 6 7 *8*
#Use (i+1)%4 == 0 to detect bad fourth interpolated measurement
i1 = 0
i2 = 0
i3 = 0
for i in range(0,len(MCTInterpList)):
    if ((i+1) % 12 != 0):
        if str(s1List[i]) != "nan" and ((i1+1) % 4 != 0):
            s1ListADJ.append(s1List[i])
            MCTInterpListS1.append(MCTInterpList[i])
        if str(s2List[i]) != "nan" and ((i2+1) % 4 != 0):
            s2ListADJ.append(s2List[i])
            MCTInterpListS2.append(MCTInterpList[i])
        if str(s3List[i]) != "nan" and ((i3+1) % 4 != 0):
            s3ListADJ.append(s3List[i])
            MCTInterpListS3.append(MCTInterpList[i])

#fixing:
for i in range(0,10):
    print(str(i) + ": S1T,S1R = " + str(MCTInterpListS1[i]) + "," + str(s1ListADJ[i]))
    #print("S2T,S2R = " + str(MCTInterpListS2[i]) + "," + str(s2ListADJ[i]))
    print(str(i) + ": S3T,S3R = " + str(MCTInterpListS3[i]) + "," + str(s3ListADJ[i]))


pltfig = plt.figure()
plt.grid() #Turns on gridlines
ax = plt.gca()
#print(str(len(MCTInterpListS1)) + "," + str(len(s1ListADJ)))
#print MCTInterpListS1
#print s1ListADJ
s1plt = ax.scatter(MCTInterpListS1,s1ListADJ,c='k',s=5,label=s1hdr)
s2plt = ax.scatter(MCTInterpListS2,s2ListADJ,c='r',s=5,label=s2hdr)
s3plt = ax.scatter(MCTInterpListS3,s3ListADJ,c='b',s=5,label=s3hdr)
ax.set_title("Resistances vs. Temperature")
ax.set_xlabel("Temperature [K]")
ax.set_ylabel("Resistance [$\Omega$]")
ax.legend()
plt.show()
