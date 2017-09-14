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

        self.SetBindings()

    #def BUTTONCLICKEDFUNC(self):

    def SetBindings(self):
        #Bindings:
        #self.BUTTON.clicked.connect(self.BUTTONCLICKEDFUNC)

        #Settings Widgets
        self.ui.measurementpasses.setValue( self.LSHDev.scanner["scannerpasses"])
        self.ui.thermalizationtime.setText( str(self.LSHDev.timeConstants["t_therm"]))
        self.ui.switchingtime.setText( str(self.LSHDev.timeConstants["t_switch"]))
        #Serial Related Widgets
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
        self.ui.saveinibutton.clicked.connect(self.SaveToINI)
        self.ui.abortbutton.clicked.connect(self.EndMeas)
        self.ui.interpolatebutton.clicked.connect(self.InterpolateCSV)
        self.ui.plotbutton.clicked.connect(self.PlotCSV)
        self.ui.taskprogressbar.setValue(0)
        self.ui.totalprogressbar.setValue(0)
        self.ui.CurrentTask.setText("Waiting to Connect to LS372...")
    def SaveToDictionaries(self):
        #Save Settings to Dictionaries:
        #Serial Related Widgets
        self.LSHDev.serialcfg["serialport"] = self.ui.serialportport.currentText()
        self.LSHDev.serialcfg["baudrate"] = self.ui.serialportbaud.text()
        #Settings Widgets
        self.LSHDev.scanner["scannerpasses"] = self.ui.measurementpasses.value()
        self.LSHDev.timeConstants["t_therm"] = self.ui.thermalizationtime.text()
        self.LSHDev.timeConstants["t_switch"] = self.ui.switchingtime.text()
        #Heater:
        self.LSHDev.sampleheater["initpc"] = self.ui.htrinit.text()
        self.LSHDev.sampleheater["finalpc"] = self.ui.htrfinal.text()
        self.LSHDev.sampleheater["deltapc"] = self.ui.htrdelta.text()
        self.LSHDev.sampleheater["resistance"] = self.ui.htrresistance.text()
        self.LSHDev.sampleheater["initpc"] = self.ui.htrmaxcurrent.text()
        self.LSHDev.sampleheater["range"] = self.ui.htrrange.currentIndex()
        #MCThermo Widgets
        self.LSHDev.mcthermo["channel"] = self.ui.mcthermochannel.value()
        self.LSHDev.mcthermo["t_dwell"] = self.ui.mcthermodwell.text()
        self.LSHDev.mcthermo["t_pause"] = self.ui.mcthermopause.text()
        self.LSHDev.mcthermo["t_settle"] = self.ui.mcthermosettle.text()
        #S1 Widgets
        self.LSHDev.sample1["channel"] = self.ui.sample1channel.value()
        self.LSHDev.sample1["description"] = self.ui.sample1description.text()
        self.LSHDev.sample1["t_dwell"] = self.ui.sample1dwell.text()
        self.LSHDev.sample1["t_pause"] = self.ui.sample1pause.text()
        self.LSHDev.sample1["t_settle"] = self.ui.sample1settle.text()
        #S2 Widgets
        self.LSHDev.sample2["channel"] = self.ui.sample2channel.value()
        self.LSHDev.sample2["description"] = self.ui.sample2description.text()
        self.LSHDev.sample2["t_dwell"] = self.ui.sample2dwell.text()
        self.LSHDev.sample2["t_pause"] = self.ui.sample2pause.text()
        self.LSHDev.sample2["t_settle"] = self.ui.sample2settle.text()
        #S3 Widgets
        self.LSHDev.sample3["channel"] = self.ui.sample3channel.value()
        self.LSHDev.sample3["description"] = self.ui.sample3description.text()
        self.LSHDev.sample3["t_dwell"] = self.ui.sample3dwell.text()
        self.LSHDev.sample3["t_pause"] = self.ui.sample3pause.text()
        self.LSHDev.sample3["t_settle"] = self.ui.sample3settle.text()
    def SaveToINI(self):
        #Save Settings to INI file:
        #self.LSHDev.parser.set(SECTION,VAR,VALUE)
        #Serial Related Widgets
        self.LSHDev.parser.set("connection", "serialport", self.ui.serialportport.currentText())
        self.LSHDev.parser.set("connection", "serialport", self.ui.serialportbaud.text())
        #Settings Widgets
        self.LSHDev.parser.set("scanner", "scannerpasses", str(self.ui.measurementpasses.value()))
        self.LSHDev.parser.set("timeconstants", "t_therm", str(self.ui.thermalizationtime.text()))
        self.LSHDev.parser.set("timeconstants", "t_switch", str(self.ui.switchingtime.text()))
        #Heater:
        self.LSHDev.parser.set("sampleheater", "initpc", str(self.ui.htrinit.text()))
        self.LSHDev.parser.set("sampleheater", "finalpc", str(self.ui.htrfinal.text()))
        self.LSHDev.parser.set("sampleheater", "deltapc", str(self.ui.htrdelta.text()))
        self.LSHDev.parser.set("sampleheater", "resistance", str(self.ui.htrresistance.text()))
        self.LSHDev.parser.set("sampleheater", "maxcurrent", str(self.ui.htrmaxcurrent.text()))
        self.LSHDev.parser.set("sampleheater", "range", str(self.ui.htrrange.currentIndex()))
        #MCThermo Widgets
        self.LSHDev.parser.set("mcthermometer", "channel", str(self.ui.mcthermochannel.value()))
        self.LSHDev.parser.set("mcthermometer", "t_dwell", str(self.ui.mcthermodwell.text()))
        self.LSHDev.parser.set("mcthermometer", "t_pause", str(self.ui.mcthermopause.text()))
        self.LSHDev.parser.set("mcthermometer", "t_settle", str(self.ui.mcthermosettle.text()))
        #S1 Widgets
        self.LSHDev.parser.set("sample1", "channel", str(self.ui.sample1channel.value()))
        self.LSHDev.parser.set("sample1", "description", str(self.ui.sample1description.text()))
        self.LSHDev.parser.set("sample1", "t_dwell", str(self.ui.sample1dwell.text()))
        self.LSHDev.parser.set("sample1", "t_pause", str(self.ui.sample1pause.text()))
        self.LSHDev.parser.set("sample1", "t_settle", str(self.ui.sample1settle.text()))
        #S2 Widgets
        self.LSHDev.parser.set("sample2", "channel", str(self.ui.sample2channel.value()))
        self.LSHDev.parser.set("sample2", "description", str(self.ui.sample2description.text()))
        self.LSHDev.parser.set("sample2", "t_dwell", str(self.ui.sample2dwell.text()))
        self.LSHDev.parser.set("sample2", "t_pause", str(self.ui.sample2pause.text()))
        self.LSHDev.parser.set("sample2", "t_settle", str(self.ui.sample2settle.text()))
        #S3 Widgets
        self.LSHDev.parser.set("sample3", "channel", str(self.ui.sample3channel.value()))
        self.LSHDev.parser.set("sample3", "description", str(self.ui.sample3description.text()))
        self.LSHDev.parser.set("sample3", "t_dwell", str(self.ui.sample3dwell.text()))
        self.LSHDev.parser.set("sample3", "t_pause", str(self.ui.sample3pause.text()))
        self.LSHDev.parser.set("sample3", "t_settle", str(self.ui.sample3settle.text()))

        with open(self.LSHDev.inifname,'wb') as configfile:
            self.LSHDev.parser.write(self.LSHDev.inifname)

    #Serial Connection Event Handlers
    def serialConnect(self):#Evt Handler for serial connect button
        self.LSHDev.ser.port = self.ui.serialportport.currentText()
        self.LSHDev.ser.baudrate = self.ui.serialportbaud.text()
        self.LSHDev.ser.open()

    def serialDisconnect(self):
        self.LSHDev.close()
    def StartMeas(self):
        self.serialConnect() #Connect to device
        self.SaveToDictionaries() #Sets parameters shown in Quick Settings to be used by the routine.
        self.MeasureLoop()        #Then run measurement routine
        self.serialDisconnect() #then disconnect from serial port.
    def MeasureLoop(self):
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
