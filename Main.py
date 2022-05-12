import time
import serial
import re
import subprocess as sb
import numpy as np
import pandas as pd
import pathlib 

WorkingPath = pathlib.Path(__file__).parent.resolve()

with serial.Serial() as ser:
    ser.baudrate = 115200
    ser.port = 'COM4'
    ser.timeout = 1

def readInputPins():
    ser.open()
    message = f"#1ZY\r"
    ser.write(message.encode())
    data = (ser.read(10))
    print("Endschalterverhalten ist: ", data)
    ser.close()

def runCalibration(Motor):
    ser.open()
    message = f"#{Motor}p4\r"
    ser.write(message.encode())
    ser.close()

def setJoystickMode(Motor):
    ser.open()
    time.sleep(1)
    message = f"#{Motor}p12\r"
    ser.write(message.encode())
    time.sleep(1)
    ser.close()
    #data = str(ser.read(10))
    #print("Received: ", data)
    #time.sleep(1)
def getEndschalterverhalten(Motor):
    ser.open()
    message = f"#{Motor}Zl\r"
    ser.write(message.encode())
    data = (ser.read(10))
    print("Endschalterverhalten ist: ", data)
    ser.close()

def getEndschalterbetaetigt(Motor):
    ser.open()
    message = f"#{Motor}ZY\r"
    ser.write(message.encode())
    data = (ser.read(10))
    print("Endschalter ist betätigt: ", data)
    ser.close()

def setZero(Motor):
    ser.open()
    message = f"#{Motor}D0\r"
    ser.write(message.encode())
    data = (ser.read(10))
    print("Motor ist auf 0 gesetzt: ", data)
    ser.close()
#Get Current Position of Motors
def setPositioningMode(Motor):
    ser.open()
    time.sleep(0.1)
    message = f"#{Motor}p2\r"
    ser.write(message.encode())
    time.sleep(0.1)
    data = str(ser.read(10))
    #print("Received: ", data)
    time.sleep(0.1)
    ser.close()

def getPosition(Motor):
    ser.open()
    time.sleep(0.1)
    #ser.flush()
    message = f"#{Motor}C\r"
    ser.write(message.encode())
    #print(message.encode())
    data = str(ser.read(10))
    print("Position is: ", data)
    position = int((data.split("C"))[1].split('\\')[0])
    #print("Received Message", position)
    ser.close()
    return position

#Sets Position for Motors to run to
def SetPosition(Motor, Position):
    ser.open()
    message = f"#{Motor}s{Position}\r"
    ser.write(message.encode())
    data = str(ser.read(10))
    print("Set Position as: ", data)
    ser.close()

#Starts Moving Motor
def MoveMotor(Motor):
    ser.open()
    message = f"#{Motor}A\r"
    ser.write(message.encode())
    #data = str(ser.read(10))
    ser.close()


def MoveMotorToPosition(Motor, newPosition):
    ser.open()
    message = f"#{Motor}s{newPosition}\r"
    ser.write(message.encode())
    #data = str(ser.read(10))
    #print("Set Position as: ", data)
    message = f"#{Motor}A\r"
    ser.write(message.encode())
    #data = str(ser.read(10))
    #print(data)
    ser.close()
    while(getPosition(Motor) != newPosition):
        print(f"Waiting for {Motor}")
    #time.sleep(5)

def SaveFile(fileName):
    f = open (WorkingPath / "PsMacros" / "SaveFile.psmacro", "w+")
    SavingPath = WorkingPath / "Measurements" / fileName
    f.write(rf"""<?xml version="1.0" encoding="utf-8" standalone="yes"?><document>
    <userealtime>True</userealtime>
    <event category="Interaction" time="26/04/22 15:15:35.739"> File.SaveAs.IO={SavingPath}</event>
    </document>""")
    f.close()
    PathToSaveMacro = rf'"{WorkingPath}\PsMacros\SaveFile.psmacro"'
    sb.call([WorkingPath / "BatchFiles" / "Run_SaveMacro.bat"], PathToSaveMacro) #Test this
    #time.sleep(3) probably not needed

def WriteLogFile(ChannelName, Motor1_mid, Motor2_mid):
    converterConstant = 1.25/1600 #mm per step
    stepValue = 320
    stepCounter = 5
    Motor1_max = Motor1_mid + stepCounter * stepValue
    Motor1_min = Motor1_mid - stepCounter * stepValue
    Motor1Coordinates = np.arange(Motor1_min, Motor1_max, stepValue).tolist()
    Motor2_max = Motor2_mid + stepCounter * stepValue
    Motor2_min = Motor2_mid - stepCounter * stepValue
    Motor2Coordinates = np.arange(Motor2_min, Motor2_max, stepValue)
    Motor1Coordinates_list = Motor1Coordinates*len(Motor2Coordinates)
    Motor2Coordinates_list = []
    for entries in Motor2Coordinates:
        for values in Motor1Coordinates:
            Motor2Coordinates_list.append(entries)
    #print(len(b_list), len(b), len(a_list), len(a))
    df = pd.DataFrame({'X Coordinates':Motor1Coordinates_list, 'Y Coordinates' :Motor2Coordinates_list})
    filename_list = []
    for index in range(len(df)):
        filename = ChannelName + "_" + str(index+1) + ".psdata"
        filename_list.append(filename)    
    df["X Coordinates in mm"] = df['X Coordinates'].multiply(converterConstant)
    df["Y Coordinates in mm"] = df['Y Coordinates'].multiply(converterConstant)
    df["filenames"] = filename_list
    ######SaveFileAs .csv
    return df

def RunPicoscope():
    sb.call([WorkingPath / "BatchFiles" / "RunMeasurement.bat"])
    time.sleep(4)

channel_list = ["A", "B", "C", "D"]

Motor1Values = []
Motor2Values = []
##############get Mid Values 
for channel in channel_list:
    print(f"move to Position of highest Amplitude of Channel ", channel )
    input("Press Enter to save Position")
    setPositioningMode(1)
    Motor1Values.append(getPosition(1))
    setPositioningMode(2)
    Motor2Values.append(getPosition(2))
print("Motor1Values: ", Motor1Values)
print("Motor2Values: ", Motor2Values)

input("Press Enter to Start Measuring")

for index, channel in enumerate(channel_list):
    log = WriteLogFile(channel, Motor1Values[index], Motor2Values[index])
    log.to_csv(WorkingPath / "Measurements" /  f"{channel}.csv")
    print ("Logs are: ", log)
    for index, row in log.iterrows():
        MoveMotorToPosition(1, row["X Coordinates"])
        MoveMotorToPosition(2, row["Y Coordinates"])
        RunPicoscope()
        SaveFile(row["filenames"])



#Include writing a log
