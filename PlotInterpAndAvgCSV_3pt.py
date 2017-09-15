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
nPasses = int(cfgparser.get('scanner','scannerpasses')) #Number of scanner passes

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
for i in range(0,len(MCTInterpList)):
    if str(s1List[i]) != "nan":
        s1ListADJ.append(s1List[i])
        MCTInterpListS1.append(MCTInterpList[i])
    if str(s2List[i]) != "nan":
        s2ListADJ.append(s2List[i])
        MCTInterpListS2.append(MCTInterpList[i])
    if str(s3List[i]) != "nan":
        s3ListADJ.append(s3List[i])
        MCTInterpListS3.append(MCTInterpList[i])

MCTAvgList = [] #Average Interpolated temperatures
s1AvgList = [] #List of averaged Sample 1 resistances
s2AvgList = []
s3AvgList = []
#Fill averages between ALL successive measurements in a pass for S1,S2,S3. Does not skip 4th R reading of S3
for iavg in range(0,len(s1List)):
    if (iavg+1) % nPasses == 1 and ((iavg+nPasses) <= len(s1ListADJ)):
        s1sum = 0
        s2sum = 0
        s3sum = 0
        for i in range(0,nPasses): #sum all samples within pass
            s1sum += s1ListADJ[iavg+i]
            s2sum += s2ListADJ[iavg+i]
            s3sum += s3ListADJ[iavg+i]
        s1AvgList.append(s1sum/nPasses)
        s2AvgList.append(s2sum/nPasses)
        s3AvgList.append(s3sum/nPasses)


#Average Temperature over measurements:
for iavg in range(0,len(MCTList)):
    if ((iavg+1) % (nPasses*nChannels)) == 1 and ((iavg+(nPasses*nChannels)) <= len(MCTList)):
        print iavg
        MCTListsum = 0
        for isum in range(0,nPasses*nChannels): #sum all samples within pass
            MCTListsum += MCTList[iavg+isum]
        MCTAvgList.append(MCTListsum/(nPasses*nChannels))

pltfig = plt.figure()
plt.grid() #Turns on gridlines
ax = plt.gca()
#print(str(len(MCTInterpListS1)) + "," + str(len(s1ListADJ)))
#print MCTInterpListS1
#print s1ListADJ
s1plt = ax.scatter(MCTInterpListS1,s1ListADJ,c='k',s=5,label=s1hdr)
s2plt = ax.scatter(MCTInterpListS2,s2ListADJ,c='r',s=5,label=s2hdr)
s3plt = ax.scatter(MCTInterpListS3,s3ListADJ,c='b',s=5,label=s3hdr)
s1plta = ax.plot(MCTAvgList,s1AvgList,c='k',label=s1hdr)
s2plta = ax.plot(MCTAvgList,s2AvgList,c='r',label=s2hdr)
s3plta = ax.plot(MCTAvgList,s3AvgList,c='b',label=s3hdr)
ax.set_title("Resistances vs. Temperature")
ax.set_xlabel("Temperature [K]")
ax.set_ylabel("Resistance [$\Omega$]")
ax.legend()
plt.show()
