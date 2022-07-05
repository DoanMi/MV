# MV
Abrasterung mittels Traverse
## Needed Libraries:
pip install string is included for all non standard libraries. Rest is already included in the standard library of the Python installation.
  * time
  * serial `pip install pyserial`
  * re
  * subprocess
  * numpy `pip install numpy`
  * pandas `pip install pandas`
  * pathlib
  * PicoScopeSDK downloaded from Picoscope webpage
    * Download SDK Passage from [here](https://www.picotech.com/downloads)
    * Set up driver bindings according to [this](https://github.com/picotech/picosdk-python-wrappers#installing-the-python-driver-bindings) tutorial
# Functions
## Main
### *MoveMotorToPosition*(Motor = 1 or 2, newPosition)
Moves `Motor` to given `newPosition`.
### *getPosition*(Motor = 1 or 2)
Returns the current Position of the `Motor` as number of steps.
### *WriteLogFile*(PointsX, PointsY, Resolution = 0.1, RadiusX = 0.5, RadiusY =1)
Returns a dataframe with a grid coordinates around the Points defined by `PointsX` and `PointsY`. The dataframe columns are as follows:  
| Column Name | Description |
| ------------- | ------------- |
| X Coordinates | List of X Coordinates in Revolutions (of stepper motor) |
| Y Coordinates | List of X Coordinates in Revolutions (of stepper motor) |
| X Coordinates in mm | List of X Coordinates in Millimeters from absolute zero |
| Y Coordinates in mm | List of Y Coordinates in Millimeters from absolute zero |
| filenames | psdata file from each measurement at each point in the grid. Goes From 0.psdata to n.psadata |

`PointsX`, `PointsY` are lists of coordinates.  
`Resolution` defines grid distance.  
`RadiusX`, `RadiusY` defines distance/2 from each point to edge of grid. 
### *setPositioningMode*(Motor = 1 or 2)
set `Motor` to be positioned by coordinate input in contrast to joystick input.
### *setJoystickMode*(Motor = 1 or 2)
set `Motor` to be positioned by joystick input in contrast to coordinate input.
### *setZero*(Motor = 1 or 2)
set current `Motor` position to zero
## Helper Picoscope
### *openUnit*(ChannelNumber = 4, ChannelRange = 7)
activates Picoscope unit.  
`ChannelNumber` defines number of Channels to record
`ChannelRange` defines voltage range for the channels  
#### Range Table
| Column Name | Description |
| ------------- | ------------- |
| PS6000_10MV | 0 |
| PS6000_100MV | 1 |
| PS6000_20MV | 2 |
| PS6000_50MV | 3 |
| PS6000_200MV | 4 |
| PS6000_500MV | 5 |
| PS6000_1V | 6 |
| PS6000_2V | 7 |
| PS6000_5V | 8 |
| PS6000_10V | 9 |
| PS6000_20V | 10 |
| PS6000_50V | 11 |
### *closeUnit*()
closes currrent Picoscope unit
