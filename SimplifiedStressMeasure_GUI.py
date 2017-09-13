import sys
import io
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
import serial
import io
from time import sleep
import numpy as np
from datetime import datetime
from configparser import ConfigParser
import LakeShore372 as ls

class StressMeasure_UI(QMainWindow):
    def __init__(self,myLS):
        QMainWindow.__init__(self)
        self.ui = uic.loadUi("LakeShore372SimplifiedStressMeasureGui.ui")
        self.LSHDev = myLS

        #Bindings:
        #self.BUTTON.clicked.connect(self.BUTTONCLICKEDFUNC)

        #Settings Widgets
        self.ui.measurementpasses.setValue( self.LSHDev.scanner["scannerpasses"])
        self.ui.thermalizationtime.setText( str(self.LSHDev.timeConstants["t_therm"]))
        self.ui.switchingtime.setText( str(self.LSHDev.timeConstants["t_switch"]))
        #Serial Related Widgets
        self.ui.serialportopen.clicked.connect(self.serialConnect)
        self.ui.serialportclose.clicked.connect(self.serialDisconnect)
        self.ui.serialportport.addItems(["COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9","COM10"])
        if LSHDev.serialcfg["serialport"] == "COM1":
            self.ui.serialportport.setCurrentIndex(1)
        elif LSHDev.serialcfg["serialport"] == "COM2":
            self.ui.serialportport.setCurrentIndex(2)
        elif LSHDev.serialcfg["serialport"] == "COM3":
            self.ui.serialportport.setCurrentIndex(3)
        elif LSHDev.serialcfg["serialport"] == "COM4":
            self.ui.serialportport.setCurrentIndex(4)
        elif LSHDev.serialcfg["serialport"] == "COM5":
            self.ui.serialportport.setCurrentIndex(5)
        elif LSHDev.serialcfg["serialport"] == "COM6":
            self.ui.serialportport.setCurrentIndex(6)
        elif LSHDev.serialcfg["serialport"] == "COM7":
            self.ui.serialportport.setCurrentIndex(7)
        elif LSHDev.serialcfg["serialport"] == "COM8":
            self.ui.serialportport.setCurrentIndex(8)
        elif LSHDev.serialcfg["serialport"] == "COM9":
            self.ui.serialportport.setCurrentIndex(9)
        elif LSHDev.serialcfg["serialport"] == "COM10":
            self.ui.serialportport.setCurrentIndex(10)
        self.ui.serialportbaud.setText( str(self.LSHDev.serialcfg["baudrate"]))


        #Heater Widgets
        self.ui.htrrange.addItems(["OFF","31.6 uA","100 uA","316 uA","1.00 mA","3.16 mA","10.0 mA","31.6 mA","100 mA"])
        self.ui.htrinit.setText( str(self.LSHDev.sampleheater["initpc"]))
        self.ui.htrfinal.setText( str(self.LSHDev.sampleheater["finalpc"]))
        self.ui.htrdelta.setText( str(self.LSHDev.sampleheater["deltapc"]))
        self.ui.htrresistance.setText( str(self.LSHDev.sampleheater["resistance"]))
        self.ui.htrmaxcurrent.setText( str(self.LSHDev.sampleheater["initpc"]))
        self.ui.htrrange.setCurrentIndex(self.LSHDev.sampleheater["range"])
        #MCThermo Widgets
        self.ui.mcthermochannel.setValue( self.LSHDev.mcthermo["channel"])
        self.ui.mcthermodwell.setText( str(self.LSHDev.mcthermo["t_dwell"]))
        self.ui.mcthermopause.setText( str(self.LSHDev.mcthermo["t_pause"]))
        self.ui.mcthermosettle.setText( str(self.LSHDev.mcthermo["t_settle"]))
        #S1 Widgets
        self.ui.sample1channel.setValue( self.LSHDev.sample1["channel"])
        self.ui.sample1description.setText( str(self.LSHDev.sample1["description"]).strip('\"'))
        self.ui.sample1dwell.setText( str(self.LSHDev.sample1["t_dwell"]))
        self.ui.sample1pause.setText( str(self.LSHDev.sample1["t_pause"]))
        self.ui.sample1settle.setText( str(self.LSHDev.sample1["t_settle"]))
        #S2 Widgets
        self.ui.sample2channel.setValue( self.LSHDev.sample2["channel"])
        self.ui.sample2description.setText( str(self.LSHDev.sample2["description"]).strip('\"'))
        self.ui.sample2dwell.setText( str(self.LSHDev.sample2["t_dwell"]))
        self.ui.sample2pause.setText( str(self.LSHDev.sample2["t_pause"]))
        self.ui.sample2settle.setText( str(self.LSHDev.sample2["t_settle"]))
        #S3 Widgets
        self.ui.sample3channel.setValue( self.LSHDev.sample3["channel"])
        self.ui.sample3description.setText( str(self.LSHDev.sample3["description"]).strip('\"'))
        self.ui.sample3dwell.setText( str(self.LSHDev.sample3["t_dwell"]))
        self.ui.sample3pause.setText( str(self.LSHDev.sample3["t_pause"]))
        self.ui.sample3settle.setText( str(self.LSHDev.sample3["t_settle"]))
        #Task Widgets
        self.ui.startbutton.clicked.connect(self.StartMeas)
        self.ui.abortbutton.clicked.connect(self.EndMeas)
        self.ui.interpolatebutton.clicked.connect(self.InterpolateCSV)
        self.ui.plotbutton.clicked.connect(self.PlotCSV)
        self.ui.taskprogressbar.setValue(0)
        self.ui.totalprogressbar.setValue(0)
        self.ui.CurrentTask.setText("Waiting to Connect to LS372...")

    #def BUTTONCLICKEDFUNC(self):

    #Serial Connection Event Handlers
    def serialConnect(self):#Evt Handler for serial connect button

        port = self.ui.serialportport.currentText()
        baud = self.ui.serialportbaud.text()
        self.LSHDev.open()

    def serialDisconnect(self):
        return 0
    def StartMeas(self):

        #Must convert all below to assignments via getText (or whatever gets text)
        #Save Settings to Dictionaries:
        #Serial Related Widgets
        self.ui.serialportbaud.setText( str(self.LSHDev.serialcfg["baudrate"]))
        #Settings Widgets
        self.ui.measurementpasses.setValue( self.LSHDev.scanner["scannerpasses"])
        self.ui.thermalizationtime.setText( str(self.LSHDev.timeConstants["t_therm"]))
        self.ui.switchingtime.setText( str(self.LSHDev.timeConstants["t_switch"]))
        #Heater:
        self.ui.htrinit.setText( str(self.LSHDev.sampleheater["initpc"]))
        self.ui.htrfinal.setText( str(self.LSHDev.sampleheater["finalpc"]))
        self.ui.htrdelta.setText( str(self.LSHDev.sampleheater["deltapc"]))
        self.ui.htrresistance.setText( str(self.LSHDev.sampleheater["resistance"]))
        self.ui.htrmaxcurrent.setText( str(self.LSHDev.sampleheater["initpc"]))
        self.ui.htrrange.setCurrentIndex(self.LSHDev.sampleheater["range"])
        #MCThermo Widgets
        self.ui.mcthermochannel.setValue( self.LSHDev.mcthermo["channel"])
        self.ui.mcthermodwell.setText( str(self.LSHDev.mcthermo["t_dwell"]))
        self.ui.mcthermopause.setText( str(self.LSHDev.mcthermo["t_pause"]))
        self.ui.mcthermosettle.setText( str(self.LSHDev.mcthermo["t_settle"]))
        #S1 Widgets
        self.ui.sample1channel.setValue( self.LSHDev.sample1["channel"])
        self.ui.sample1description.setText( str(self.LSHDev.sample1["description"]).strip('\"'))
        self.ui.sample1dwell.setText( str(self.LSHDev.sample1["t_dwell"]))
        self.ui.sample1pause.setText( str(self.LSHDev.sample1["t_pause"]))
        self.ui.sample1settle.setText( str(self.LSHDev.sample1["t_settle"]))
        #S2 Widgets
        self.ui.sample2channel.setValue( self.LSHDev.sample2["channel"])
        self.ui.sample2description.setText( str(self.LSHDev.sample2["description"]).strip('\"'))
        self.ui.sample2dwell.setText( str(self.LSHDev.sample2["t_dwell"]))
        self.ui.sample2pause.setText( str(self.LSHDev.sample2["t_pause"]))
        self.ui.sample2settle.setText( str(self.LSHDev.sample2["t_settle"]))
        #S3 Widgets
        self.ui.sample3channel.setValue( self.LSHDev.sample3["channel"])
        self.ui.sample3description.setText( str(self.LSHDev.sample3["description"]).strip('\"'))
        self.ui.sample3dwell.setText( str(self.LSHDev.sample3["t_dwell"]))
        self.ui.sample3pause.setText( str(self.LSHDev.sample3["t_pause"]))
        self.ui.sample3settle.setText( str(self.LSHDev.sample3["t_settle"]))

        #Then open the connection,

        #Then run measurement routine
        return 0

    def EndMeas(self):
        return 0

    def InterpolateCSV(self):
        return 0

    def PlotCSV(self):
        return 0







LSHDev = ls.LakeShore372Device() #Create instance of LakeShore372Device
LSHDev.getConfig('config.ini') #Load configuration/ini file

LSHDataFile = open("testdata.csv",'w') #Open the file
LSHData = ls.LakeShore372Data(LSHDataFile,LSHDev.sample1["description"],LSHDev.sample2["description"],LSHDev.sample3["description"]) #Pass file to data handler class
print("o  Datafile Created.")

#GUI Initialization


app = QApplication(sys.argv)
myWindow = StressMeasure_UI(LSHDev)
myWindow.ui.show()
app.exec_()
