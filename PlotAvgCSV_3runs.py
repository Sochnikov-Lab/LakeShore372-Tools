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
MCThdr = "MCTemp"
MCTInterphdr = MCThdr + "_Interp"
MCRhdr = "MCResist"
s1hdr = str(cfgparser.get('sample1','description')).strip('\"') #Sample 1 Header
s2hdr = str(cfgparser.get('sample2','description')).strip('\"') #Sample 2 Header
s3hdr = str(cfgparser.get('sample3','description')).strip('\"') #Sample 3 Header

#Read in CSV file as lists:
argfilename_1 = "20170912-162258_htr655.csv" #Run 1
argfilename_2 = "20170914-212626_htr655_30uA_2.csv" #Run 2
argfilename_3 = "20170917-030521_htr655_10uA.csv" #Run 3

dataframe_1 = pd.read_csv(argfilename_1)
dataframe_2 = pd.read_csv(argfilename_2)
dataframe_3 = pd.read_csv(argfilename_3)

#Run 1:
MCTList_1 = dataframe_1[MCThdr] #List of MC temperatures
s1List_1 = dataframe_1[s1hdr] #List of resistances for Sample 1
s2List_1 = dataframe_1[s2hdr] #List of resistances for Sample 2
s3List_1 = dataframe_1[s3hdr] #List of resistances for Sample 3
#Adjust lists to not include NaN:
s1ListADJ_1 = []
s2ListADJ_1 = []
s3ListADJ_1 = []
for i in range(0,len(MCTList_1)):
    #if ((i+1) % nPasses*nChannels != 0):
    if str(s1List_1[i]) != "nan":
        s1ListADJ_1.append(s1List_1[i])
    if str(s2List_1[i]) != "nan":
        s2ListADJ_1.append(s2List_1[i])
    if str(s3List_1[i]) != "nan":
        s3ListADJ_1.append(s3List_1[i])
MCTAvgList_1 = [] #Average Interpolated temperatures
s1AvgList_1 = [] #List of averaged Sample 1 resistances
s2AvgList_1 = []
s3AvgList_1 = []
#Fill averages between ALL successive measurements in a pass for S1,S2,S3. Does not skip 4th R reading of S3
for iavg in range(0,len(s1List_1)):
    if (iavg+1) % nPasses == 1 and ((iavg+nPasses) <= len(s1ListADJ_1)):
        s1sum = 0
        s2sum = 0
        s3sum = 0
        for i in range(0,nPasses): #sum all samples within pass
            s1sum += s1ListADJ_1[iavg+i]
            s2sum += s2ListADJ_1[iavg+i]
            s3sum += s3ListADJ_1[iavg+i]
        s1AvgList_1.append(s1sum/nPasses)
        s2AvgList_1.append(s2sum/nPasses)
        s3AvgList_1.append(s3sum/nPasses)
#Average Temperature over measurements:
for iavg in range(0,len(MCTList_1)):
    if ((iavg+1) % (nPasses*nChannels)) == 1 and ((iavg+(nPasses*nChannels)) <= len(MCTList_1)):
        print iavg
        MCTListsum = 0
        for isum in range(0,nPasses*nChannels): #sum all samples within pass
            MCTListsum += MCTList_1[iavg+isum]
        MCTAvgList_1.append(MCTListsum/(nPasses*nChannels))

#Run 2:
MCTList_2 = dataframe_2[MCThdr] #List of MC temperatures
s1List_2 = dataframe_2[s1hdr] #List of resistances for Sample 1
s2List_2 = dataframe_2[s2hdr] #List of resistances for Sample 2
s3List_2 = dataframe_2[s3hdr] #List of resistances for Sample 3
#Adjust lists to not include NaN:
s1ListADJ_2 = []
s2ListADJ_2 = []
s3ListADJ_2 = []
for i in range(0,len(MCTList_2)):
    #if ((i+1) % nPasses*nChannels != 0):
    if str(s1List_2[i]) != "nan":
        s1ListADJ_2.append(s1List_2[i])
    if str(s2List_2[i]) != "nan":
        s2ListADJ_2.append(s2List_2[i])
    if str(s3List_2[i]) != "nan":
        s3ListADJ_2.append(s3List_2[i])
MCTAvgList_2 = [] #Average Interpolated temperatures
s1AvgList_2 = [] #List of averaged Sample 1 resistances
s2AvgList_2 = []
s3AvgList_2 = []
#Fill averages between ALL successive measurements in a pass for S1,S2,S3. Does not skip 4th R reading of S3
for iavg in range(0,len(s1List_1)):
    if (iavg+1) % nPasses == 1 and ((iavg+nPasses) <= len(s1ListADJ_2)):
        s1sum = 0
        s2sum = 0
        s3sum = 0
        for i in range(0,nPasses): #sum all samples within pass
            s1sum += s1ListADJ_2[iavg+i]
            s2sum += s2ListADJ_2[iavg+i]
            s3sum += s3ListADJ_2[iavg+i]
        s1AvgList_2.append(s1sum/nPasses)
        s2AvgList_2.append(s2sum/nPasses)
        s3AvgList_2.append(s3sum/nPasses)
#Average Temperature over measurements:
for iavg in range(0,len(MCTList_2)):
    if ((iavg+1) % (nPasses*nChannels)) == 1 and ((iavg+(nPasses*nChannels)) <= len(MCTList_2)):
        print iavg
        MCTListsum = 0
        for isum in range(0,nPasses*nChannels): #sum all samples within pass
            MCTListsum += MCTList_2[iavg+isum]
        MCTAvgList_2.append(MCTListsum/(nPasses*nChannels))

#Run 3:
MCTList_3 = dataframe_3[MCThdr] #List of MC temperatures
s1List_3 = dataframe_3[s1hdr] #List of resistances for Sample 1
s2List_3 = dataframe_3[s2hdr] #List of resistances for Sample 2
s3List_3 = dataframe_3[s3hdr] #List of resistances for Sample 3
#Adjust lists to not include NaN:
s1ListADJ_3 = []
s2ListADJ_3 = []
s3ListADJ_3 = []
for i in range(0,len(MCTList_3)):
    #if ((i+1) % nPasses*nChannels != 0):
    if str(s1List_3[i]) != "nan":
        s1ListADJ_3.append(s1List_3[i])
    if str(s2List_3[i]) != "nan":
        s2ListADJ_3.append(s2List_3[i])
    if str(s3List_3[i]) != "nan":
        s3ListADJ_3.append(s3List_3[i])
MCTAvgList_3 = [] #Average Interpolated temperatures
s1AvgList_3 = [] #List of averaged Sample 1 resistances
s2AvgList_3 = []
s3AvgList_3 = []
#Fill averages between ALL successive measurements in a pass for S1,S2,S3. Does not skip 4th R reading of S3
for iavg in range(0,len(s1List_3)):
    if (iavg+1) % nPasses == 1 and ((iavg+nPasses) <= len(s1ListADJ_3)):
        s1sum = 0
        s2sum = 0
        s3sum = 0
        for i in range(0,nPasses): #sum all samples within pass
            s1sum += s1ListADJ_3[iavg+i]
            s2sum += s2ListADJ_3[iavg+i]
            s3sum += s3ListADJ_3[iavg+i]
        s1AvgList_3.append(s1sum/nPasses)
        s2AvgList_3.append(s2sum/nPasses)
        s3AvgList_3.append(s3sum/nPasses)
#Average Temperature over measurements:
for iavg in range(0,len(MCTList_3)):
    if ((iavg+1) % (nPasses*nChannels)) == 1 and ((iavg+(nPasses*nChannels)) <= len(MCTList_3)):
        print iavg
        MCTListsum = 0
        for isum in range(0,nPasses*nChannels): #sum all samples within pass
            MCTListsum += MCTList_3[iavg+isum]
        MCTAvgList_3.append(MCTListsum/(nPasses*nChannels))

pltfig = plt.figure()
plt.grid() #Turns on gridlines
ax = plt.gca()
#print(str(len(MCTInterpListS1)) + "," + str(len(s1ListADJ)))
#print MCTInterpListS1
#print s1ListADJ

#Average, Run 1:
#avg Data, Run 1:
s1plt = ax.plot(MCTAvgList_1,s1AvgList_1,c='k',mec='k',mfc='k',marker='o',label=s1hdr + "_30uA_20170912_avg")
s2plt = ax.plot(MCTAvgList_1,s2AvgList_1,c='r',mec='r',mfc='r',marker='o',label=s2hdr + "_30uA_20170912_avg")
s3plt = ax.plot(MCTAvgList_1,s3AvgList_1,c='b',mec='b',mfc='b',marker='o',label=s3hdr + "_30uA_20170912_avg")

#avg Data, Run 2:
s1plt = ax.plot(MCTAvgList_2,s1AvgList_2,c='k',mec='k',mfc='none',marker='s',linestyle="--",label=s1hdr + "_30uA_20170914_avg")
s2plt = ax.plot(MCTAvgList_2,s2AvgList_2,c='r',mec='r',mfc='none',marker='s',linestyle="--",label=s2hdr + "_30uA_20170914_avg")
s3plt = ax.plot(MCTAvgList_2,s3AvgList_2,c='b',mec='b',mfc='none',marker='s',linestyle="--",label=s3hdr + "_30uA_20170914_avg")

#avg Data, Run 3:
s1plt = ax.plot(MCTAvgList_3,s1AvgList_3,c='k',mec='k',mfc='none',marker='d',linestyle=":",label=s1hdr + "_30uA_20170917_avg")
s2plt = ax.plot(MCTAvgList_3,s2AvgList_3,c='r',mec='r',mfc='none',marker='d',linestyle=":",label=s2hdr + "_30uA_20170917_avg")
s3plt = ax.plot(MCTAvgList_3,s3AvgList_3,c='b',mec='b',mfc='none',marker='d',linestyle=":",label=s3hdr + "_30uA_20170917_avg")

ax.set_title("Resistances vs. Temperature")
ax.set_xlabel("Temperature [K]")
ax.set_ylabel("Resistance [$\Omega$]")
ax.legend()
plt.show()
