import serial
import io
from configparser import ConfigParser

cfgparser = ConfigParser()
cfgparser.read('config.ini')

#Connection configuration
serial_cfg = {
    "port":str(cfgparser.get('connection','serialport')),
    "baud":int(cfgparser.get('connection','baudrate'))
}
#sample heater configuration
sh_cfg = {
    "resistance":float(cfgparser.get('sampleheater','sh_resistanceOhms')),
    "maxcurrent":float(cfgparser.get('sampleheater','sh_maxcurrentAmps')),
    "shrange":float(cfgparser.get('sampleheater','sh_rangemilliAmps')),
    "disp":int(cfgparser.get('sampleheater','sh_disp'))
}
#Scanner Configuration
scanner_cfg = {
    "control":int(cfgparser.get('scanner','control_ch')),
    "stress":int(cfgparser.get('scanner','stress_ch')),
    "autoscan":int(cfgparser.get('scanner','autoscan'))
}

print("===LakeShore Temperature Ramping Interface===")
print("o  Configuration Loaded...")
print("     ->Serial Port: " + serial_cfg["port"] + "/" + str(serial_cfg["baud"]))
print("     ->Control sample on channel:  " + str(scanner_cfg["control"]))
print("     ->Stressed sample on channel: " + str(scanner_cfg["stress"]))
print("     ->Autoscan is: " + if(scanner_cfg["autoscan"] == 1))
