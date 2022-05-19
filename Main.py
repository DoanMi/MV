import time
import serial
import re
import subprocess as sb
import numpy as np
import pandas as pd
import pathlib 
import matplotlib.pyplot as plt
import serial.tools.list_ports



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
    #data = str(ser.read(10))
    #print("Received: ", data)
    #time.sleep(0.1)
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
    PathToSaveMacro = rf"{WorkingPath}\PsMacros\SaveFile.psmacro"
    print(PathToSaveMacro)
    sb.call([WorkingPath / "BatchFiles" / "Run_SaveMacro.bat", PathToSaveMacro]) #Test this
    #time.sleep(3) probably not needed

def WriteLogFile(PointsX, PointsY, Resolution = 0.08, RadiusX = 0.5, RadiusY =1):
    converterConstant = 1.25/1600 #mm per step
    print(PointsY)
    PointsX = [converterConstant * i for i in PointsX]
    PointsY = [converterConstant * i for i in PointsY]
    print(PointsY)
    X_Max = max(PointsX) + RadiusX
    #print("X_Max is: ", X_Max)
    X_Min = min(PointsX) - RadiusX
    #print("X_min is: ", X_Min)
    steps_X = ((X_Max-X_Min) / Resolution ) +1
    #print(steps_X)
    X_Values = np.linspace(X_Min, X_Max, num = int(steps_X))
    #print("X Values are: ", X_Values)
    Y_Max = max(PointsY) + RadiusY
    #print("Y_Max is: ", Y_Max)
    Y_Min = min(PointsY) - RadiusY
    #print("Y_Min is: ", Y_Min)
    steps_Y = ((Y_Max-Y_Min) / Resolution) +1
    Y_Values = np.linspace(Y_Min, Y_Max, num = int(steps_Y))
    #print("Y Values are: ", Y_Values)
    xx, yy = np.meshgrid(X_Values, Y_Values)
    #print("XX is: ", xx, "YY is :", yy.shape)
    positions = np.vstack([xx.ravel(), yy.ravel()])
    X_Coords = positions[0].tolist()
    #print("Length before: ", len(X_Coords))
    Y_Coords = positions[1].tolist()
    #print(len(Y_Coords))
    f = plt.figure(1)
    plt.plot(X_Coords, Y_Coords, marker='o', color='r', linestyle='none')
    IdxToRemove = []
    Filename_list = []
    for index, (X_Coordinate, Y_Coordinate) in enumerate(zip(X_Coords, Y_Coords)):
        filename = str(index+1) + ".psdata"
        Filename_list.append(filename) 
        for PointX, PointY in zip(PointsX, PointsY):
            LeftPoint = PointX - RadiusX
            RightPoint = PointX + RadiusX
            BottomPoint = PointY - RadiusY
            UpperPoint = PointY + RadiusY
            if LeftPoint <= X_Coordinate <= RightPoint and BottomPoint <= Y_Coordinate <= UpperPoint:
                RemoveNumber = False
                break
            else:
                RemoveNumber = True
        if RemoveNumber == True:
            IdxToRemove.append(index)
    for idx in sorted(IdxToRemove, reverse = True):
        del X_Coords[idx]
        del Y_Coords[idx]
    #print("Length after: ", len(X_Coords))
    #print("Length after: ", len(Y_Coords))
    plt.plot(X_Coords, Y_Coords, marker='.', color='k', linestyle='none')
    g = plt.figure(2)
    X_CoordsInRevs = [round((1/converterConstant) * i) for i in X_Coords]
    Y_CoordsInRevs = [round((1/converterConstant) * i) for i in Y_Coords]
    Filename_list = [str(i+1) + ".psdata" for i, item in enumerate(X_Coords)]
    plt.plot(X_CoordsInRevs, Y_CoordsInRevs, marker='o', color='k', linestyle='none')
    plt.show()
    df = pd.DataFrame({'X Coordinates':X_CoordsInRevs, 'Y Coordinates' :Y_CoordsInRevs, 'X Coordinates in mm' :X_Coords, 'Y Coordinates in mm': Y_Coords, "filenames": Filename_list})
    return df

def RunPicoscope():
    sb.call([WorkingPath / "BatchFiles" / "RunMeasurement.bat"])
    time.sleep(4)

##---------------------------------------------------------##
WorkingPath = pathlib.Path(__file__).parent.resolve()
print([comport.description for comport in serial.tools.list_ports.comports()])
with serial.Serial() as ser:
    ser.baudrate = 115200
    ser.port = 'COM4'
    ser.timeout = 1

channel_list = ["A"] ####Modify this

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


log = WriteLogFile(Motor1Values, Motor2Values)
pathlib.Path(WorkingPath / "Measurements").mkdir(parents = True, exist_ok = True)
log.to_csv(WorkingPath / "Measurements" /  "Log.csv")
print ("Logs are: ", log)
for index, row in log.iterrows():
    MoveMotorToPosition(1, row["X Coordinates"])
    MoveMotorToPosition(2, row["Y Coordinates"])
    RunPicoscope()
    SaveFile(row["filenames"])



#Include writing a log

