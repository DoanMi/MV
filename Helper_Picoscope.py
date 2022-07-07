#
# Copyright (C) 2018-2022 Pico Technology Ltd. See LICENSE file for terms.
#
# PS6000 BLOCK MODE EXAMPLE
# This example opens a 6000 driver device, sets up two channels and a trigger then collects a block of data.
# This data is then plotted as mV against time in ns.

import ctypes
import numpy as np
from picosdk.ps6000 import ps6000 as ps
#import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok
import pandas as pd
import time

# Create chandle and status ready for use
chandle = ctypes.c_int16()
status = {}

# Open 6000 series PicoScope
# Returns handle to chandle for use in future API functions
def openUnit(ChannelNumber = 4, ChannelRange = 7):
    status["openunit"] = ps.ps6000OpenUnit(ctypes.byref(chandle), None)
    assert_pico_ok(status["openunit"])

    # Set up channel A
    # handle = chandle
    # channel = PS6000_CHANNEL_A = 0
    # enabled = 1
    # coupling type = PS6000_DC = 1
    # range = PS6000_2V = 7
    # analogue offset = 0 V
    # bandwidth limiter = PS6000_BW_FULL = 0
    chARange = ChannelRange
    status["setChA"] = ps.ps6000SetChannel(chandle, 0, 1, 2, chARange, 0, 0)
    assert_pico_ok(status["setChA"])

    # Set up channel B
    # handle = chandle
    # channel = PS6000_CHANNEL_B = 1
    # enabled = 1
    # coupling type = PS6000_DC = 1
    # range = PS6000_2V = 7
    # analogue offset = 0 V
    # bandwidth limiter = PS6000_BW_FULL = 0
    chBRange = ChannelRange
    status["setChB"] = ps.ps6000SetChannel(chandle, 1, 1, 2, chBRange, 0, 0)
    assert_pico_ok(status["setChB"])
    if ChannelNumber == 4: 
        # Set up channel C
        # handle = chandle
        # channel = PS6000_CHANNEL_B = 1
        # enabled = 1
        # coupling type = PS6000_DC = 1
        # range = PS6000_2V = 7
        # analogue offset = 0 V
        # bandwidth limiter = PS6000_BW_FULL = 0
        chCRange = ChannelRange
        status["setChC"] = ps.ps6000SetChannel(chandle, 2, 1, 2, chCRange, 0, 0)
        assert_pico_ok(status["setChC"])

        # Set up channel D
        # handle = chandle
        # channel = PS6000_CHANNEL_B = 1
        # enabled = 1
        # coupling type = PS6000_DC = 1
        # range = PS6000_2V = 7
        # analogue offset = 0 V
        # bandwidth limiter = PS6000_BW_FULL = 0
        chDRange = ChannelRange
        status["setChD"] = ps.ps6000SetChannel(chandle, 3, 1, 2, chDRange, 0, 0)
        assert_pico_ok(status["setChD"])
# Set up single trigger
# handle = chandle
# enabled = 1
# source = PS6000_CHANNEL_A = 0
# threshold = 64 ADC counts
# direction = PS6000_RISING = 2
# delay = 0 s
# auto Trigger = 1000 ms
def setTrigger():
    status["trigger"] = ps.ps6000SetSimpleTrigger(chandle, 0, 0, 64, 2, 0, 1000)
    assert_pico_ok(status["trigger"])

# Set number of pre and post trigger samples to be collected
def runMeasurement(MeasurementMode, ChannelNumber = 4, sampleSize = 6250000,  timebase = 4, channelRange = 7):
    preTriggerSamples = 0
    postTriggerSamples = sampleSize
    maxSamples = preTriggerSamples + postTriggerSamples

    # Get timebase information
    # Warning: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.  
    # To access these Timebases, set any unused analogue channels to off.
    # handle = chandle
    # timebase = 8 = timebase
    # noSamples = maxSamples
    # pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
    # oversample = 1
    # pointer to maxSamples = ctypes.byref(returnedMaxSamples)
    # segment index = 0
    # timebase = 4 => 3.2ns Abtastintervall
    timeIntervalns = ctypes.c_float()
    returnedMaxSamples = ctypes.c_int32()
    status["getTimebase2"] = ps.ps6000GetTimebase2(chandle, timebase, maxSamples, ctypes.byref(timeIntervalns), 1, ctypes.byref(returnedMaxSamples), 0)
    assert_pico_ok(status["getTimebase2"])

    # Run block capture
    # handle = chandle
    # number of pre-trigger samples = preTriggerSamples
    # number of post-trigger samples = PostTriggerSamples
    # timebase = 8 = 80 ns (see Programmer's guide for mre information on timebases)
    # oversample = 0
    # time indisposed ms = None (not needed in the example)
    # segment index = 0
    # lpReady = None (using ps6000IsReady rather than ps6000BlockReady)
    # pParameter = None
    status["runBlock"] = ps.ps6000RunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase, 0, None, 0, None, None)
    assert_pico_ok(status["runBlock"])

    # Check for data collection to finish using ps6000IsReady
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status["isReady"] = ps.ps6000IsReady(chandle, ctypes.byref(ready))

    # Create buffers ready for assigning pointers for data collection
    bufferAMax = (ctypes.c_int16 * maxSamples)()
    bufferAMin = (ctypes.c_int16 * maxSamples)() # used for downsampling which isn't in the scope of this example
    bufferBMax = (ctypes.c_int16 * maxSamples)()
    bufferBMin = (ctypes.c_int16 * maxSamples)() # used for downsampling which isn't in the scope of this example
    if ChannelNumber == 4:
        bufferCMax = (ctypes.c_int16 * maxSamples)()
        bufferCMin = (ctypes.c_int16 * maxSamples)() # used for downsampling which isn't in the scope of this example
        bufferDMax = (ctypes.c_int16 * maxSamples)()
        bufferDMin = (ctypes.c_int16 * maxSamples)() # used for downsampling which isn't in the scope of this example

    # Set data buffer location for data collection from channel A
    # handle = chandle
    # source = PS6000_CHANNEL_A = 0
    # pointer to buffer max = ctypes.byref(bufferAMax)
    # pointer to buffer min = ctypes.byref(bufferAMin)
    # buffer length = maxSamples
    # ratio mode = PS6000_RATIO_MODE_NONE = 0
    status["setDataBuffersA"] = ps.ps6000SetDataBuffers(chandle, 0, ctypes.byref(bufferAMax), ctypes.byref(bufferAMin), maxSamples, 0)
    assert_pico_ok(status["setDataBuffersA"])

    # Set data buffer location for data collection from channel B
    # handle = chandle
    # source = PS6000_CHANNEL_B = 1
    # pointer to buffer max = ctypes.byref(bufferBMax)
    # pointer to buffer min = ctypes.byref(bufferBMin)
    # buffer length = maxSamples
    # ratio mode = PS6000_RATIO_MODE_NONE = 0
    status["setDataBuffersB"] = ps.ps6000SetDataBuffers(chandle, 1, ctypes.byref(bufferBMax), ctypes.byref(bufferBMin), maxSamples, 0)
    assert_pico_ok(status["setDataBuffersB"])
    
    if ChannelNumber == 4:
        status["setDataBuffersC"] = ps.ps6000SetDataBuffers(chandle, 2, ctypes.byref(bufferCMax), ctypes.byref(bufferCMin), maxSamples, 0)
        assert_pico_ok(status["setDataBuffersC"])

        status["setDataBuffersD"] = ps.ps6000SetDataBuffers(chandle, 3, ctypes.byref(bufferDMax), ctypes.byref(bufferDMin), maxSamples, 0)
        assert_pico_ok(status["setDataBuffersD"])

    # create overflow loaction
    overflow = ctypes.c_int16()
    # create converted type maxSamples
    cmaxSamples = ctypes.c_int32(maxSamples)

    # Retried data from scope to buffers assigned above
    # handle = chandle
    # start index = 0
    # pointer to number of samples = ctypes.byref(cmaxSamples)
    # downsample ratio = 1
    # downsample ratio mode = PS6000_RATIO_MODE_NONE
    # pointer to overflow = ctypes.byref(overflow))
    status["getValues"] = ps.ps6000GetValues(chandle, 0, ctypes.byref(cmaxSamples), 1, 0, 0, ctypes.byref(overflow))
    assert_pico_ok(status["getValues"])

    # find maximum ADC count value
    maxADC = ctypes.c_int16(32512)

    # convert ADC counts data to mV
    adc2mVChAMax =  adc2mV(bufferAMax, channelRange, maxADC)
    adc2mVChBMax =  adc2mV(bufferBMax, channelRange, maxADC)
    if ChannelNumber == 4:
        adc2mVChCMax =  adc2mV(bufferCMax, channelRange, maxADC)
        adc2mVChDMax =  adc2mV(bufferDMax, channelRange, maxADC)

    # Create time data
    

    status["stop"] = ps.ps6000Stop(chandle)
    assert_pico_ok(status["stop"])
    if MeasurementMode == 1: 
        if ChannelNumber == 4:
            KeyValues = {
                "MeansA" : np.mean(adc2mVChAMax), "MeansB" : np.mean(adc2mVChBMax), "MeansC" : np.mean(adc2mVChCMax), "MeansD" : np.mean(adc2mVChDMax),
                "StdA" : np.std(adc2mVChAMax), "StdB" : np.std(adc2mVChBMax), "StdC" : np.std(adc2mVChCMax), "StdD" : np.std(adc2mVChDMax),
                "MinA" : np.amin(adc2mVChAMax), "MinB" :  np.amin(adc2mVChBMax), "MinC" :  np.amin(adc2mVChCMax), "MinD" :  np.amin(adc2mVChDMax), 
                "MaxA" : np.amax(adc2mVChAMax), "MaxB" :  np.amax(adc2mVChBMax), "MaxC" :  np.amax(adc2mVChCMax), "MaxD" :  np.amax(adc2mVChDMax)
            }
        else:
            KeyValues = {
                "MeansA" : np.mean(adc2mVChAMax), "MeansB" : np.mean(adc2mVChBMax), 
                "StdA" : np.std(adc2mVChAMax), "StdB" : np.std(adc2mVChBMax), 
                "MinA" : np.amin(adc2mVChAMax), "MinB" :  np.amin(adc2mVChBMax), 
                "MaxA" : np.amax(adc2mVChAMax), "MaxB" :  np.amax(adc2mVChBMax), 
            }
        return KeyValues
    if MeasurementMode == 0:
        time = np.linspace(0, (cmaxSamples.value -1) * timeIntervalns.value, cmaxSamples.value)
        if ChannelNumber == 4:
            df = pd.DataFrame({'ValuesA': adc2mVChAMax, 'ValuesB' : adc2mVChBMax, 'ValuesC' : adc2mVChCMax, 'ValuesD' : adc2mVChDMax, "Time" : time})
        else:
            df = pd.DataFrame({'ValuesA': adc2mVChAMax, 'ValuesB' : adc2mVChBMax, "Time" : time})
        return df

    # plot data from channel A and B
    # plt.plot(time, adc2mVChAMax[:])
    # plt.plot(time, adc2mVChBMax[:])
    # plt.plot(time, adc2mVChCMax[:])
    # plt.plot(time, adc2mVChDMax[:])
    # plt.xlabel('Time (ns)')
    # plt.ylabel('Voltage (mV)')
    # plt.show()

def closeUnit():
    # Close unitDisconnect the scope
    # handle = chandle
    ps.ps6000CloseUnit(chandle)

# # display status returns
# print(status)

if __name__ == "__main__":
    openUnit()
    print(runMeasurement(1))
    time.sleep(2)
    print(runMeasurement(1))
    closeUnit()