import sys
import queue
import time
import random
import pygame
import matplotlib.pyplot as plt
import ICSView
import ICSModel
import NetworkEncoder as ne
from pymodbus.client.sync import ModbusTcpClient
import logging

#---------------------------------------------------------------------------#
# This will simply send everything logged to console
#---------------------------------------------------------------------------#

MODBUS_SLAVE = 'ms.ics.example.com'

ROOM_TEMP = 15
TIME_STEP = 1
TIME_PERIOD = 7200
WATER_LEVEL_INIT = 500000
MEGA = 1000000
HEATER_POWER = 2000 * MEGA
OUT_EXP_POWER = HEATER_POWER * 0.6
DEBUG = False

#random.seed(100)

def addPlot(rows, cols, index, plt, xVals, yVals, xLabel, yLabel):
    plt.subplot(rows, cols, index)
    plt.plot(xVals, yVals, 'r--')
    xVals.sort()
    yVals.sort()
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.axis([xVals[0], xVals[xVals.__len__() - 1],
               yVals[0], yVals[yVals.__len__() - 1] * 1.1])
    return plt

done = False

containerTest = ICSModel.Container(ROOM_TEMP, 1, WATER_LEVEL_INIT, WATER_LEVEL_INIT * 6 / 5)

nextSteam = 0
steamChamp = 0
steamMax = 0
conLower = 0
seconds = 0
points = []

# Rough value check
while seconds < TIME_PERIOD + 1:
    nextSteam = containerTest.addHeat(HEATER_POWER * TIME_STEP)
    points.append(nextSteam)
    if nextSteam != 0:
        if nextSteam > steamMax:
            steamChamp = nextSteam
            conLower = 0
        else:
            conLower += 1
            if conLower > 3:
                break
    seconds += TIME_STEP

points.sort(reverse=True)
steamMax = points[0]
powerRatio = OUT_EXP_POWER / steamMax

ICSModel = ICSModel.Model(WATER_LEVEL_INIT * 6 / 5)
ICSView = ICSView.View("True ICS State", WATER_LEVEL_INIT * 6 / 5)

seconds = 0
powerOut = 0
steamStep = 0
steamCumulative = 0
powerIn = 0

secondsPlot = []
steamStepPlot = []
steamCumulativePlot = []
waterLevelPlot = []
temperaturePlot = []
powerPlot = []

secondsPlot.append(0)
steamStepPlot.append(0)
steamCumulativePlot.append(0)
waterLevelPlot.append(ICSModel.getContainer().getWaterLevel())
temperaturePlot.append(ICSModel.getContainer().getCurrentTemp())
powerPlot.append(0)

client = ModbusTcpClient(MODBUS_SLAVE)
outputs = []

outputs = ne.modbusEncode(0, 42, 0, outputs)
write = client.write_registers(0, outputs, unit=1)
outputs = []

#Convert and send
outputs = ne.modbusEncode(0, 2, 2, outputs)
outputs = ne.modbusEncode(0, 2, 0, outputs)
#Set real values
outputs = ne.modbusEncode(ICSModel.getContainer().getWaterLevel(), 4, 4, outputs)
outputs = ne.modbusEncode(ICSModel.getContainer().getCurrentTemp(), 2, 2, outputs)
outputs = ne.modbusEncode(powerOut, 6, 2, outputs)
outputs = ne.modbusEncode(steamStep, 2, 4, outputs)
outputs = ne.modbusEncode(powerIn, 6, 2, outputs)
write = client.write_registers(0, outputs, unit=1)

client.close()
serverSeconds = -1
addFire = 0

#Source of physics, not source of what is happening
while seconds < TIME_PERIOD + 1 or done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    #only writing to and reading from slaves
    #get updates from inputs
    #Perfect attack scenario attack here - misinformation from master

    #Await response from HMI
    #print(seconds)
    while serverSeconds != 0:
        time.sleep(0.1)
        result = client.read_holding_registers(0, 21, unit=1)
    #    print(result)
    #    print(result.registers)
        addWater = ne.modbusDecode(0, 2, 2, result.registers)
        addFire = ne.modbusDecode(2, 2, 0, result.registers)
        serverSeconds = ne.modbusDecode(20, 2, 0, result.registers)
    #print(seconds)
    #Run physics
    if addFire == 1:
        powerIn = min(HEATER_POWER, powerIn * 1.02)
        powerIn = max(powerIn, 0.01 * MEGA)
        steamStep = ICSModel.addHeat(powerIn * TIME_STEP)
    elif addFire == 0 and powerIn * 0.98 / MEGA > 0.01:
        # Reduce power in
        powerIn = powerIn * 0.98
        steamStep = ICSModel.addHeat(powerIn * TIME_STEP)
    else:
        powerIn = 0
        steamStep = ICSModel.loseHeat()

    ICSModel.addWater(addWater)
    waterLevel = ICSModel.getContainer().getWaterLevel()
    temperature = ICSModel.getContainer().getCurrentTemp()
    powerOut = powerRatio * steamStep
    steamCumulative += steamStep
    overflowAmount = ICSModel.getContainer().getOverflowAmount()

    #DRAW
    ICSView.update(steamStep, steamMax, addWater, waterLevel, powerIn, powerOut, overflowAmount, temperature)

    secondsPlot.append(seconds)
    steamStepPlot.append(steamStep)
    steamCumulativePlot.append(steamCumulative)
    waterLevelPlot.append(waterLevel)
    temperaturePlot.append(temperature)
    powerPlot.append(powerOut/MEGA)

    if DEBUG:
        print("Sensor values at : ", seconds, "s")
        print("====================================")
        print("Steam OUT   :", steamStep,"kg/s")
        print("Water TEMP  :", temperature, "C")
        print("Water LEVEL :", waterLevel, "L")
        print("Power OUT   :", powerOut / MEGA, "MW")
        print("====================================")

    #Plots disp

    #Update sensors with values
    #master is only really going to care about the water level for our example
    outputs = []

    #Convert and send
    seconds += TIME_STEP
    serverSeconds = -1

    outputs = ne.modbusEncode(waterLevel, 4, 4, outputs)
    outputs = ne.modbusEncode(temperature, 2, 2, outputs)
    outputs = ne.modbusEncode(powerOut, 6, 2, outputs)
    outputs = ne.modbusEncode(steamStep, 2, 4, outputs)
    outputs = ne.modbusEncode(powerIn, 6, 2, outputs)
    outputs = ne.modbusEncode(seconds, 2, 0, outputs)

    write = client.write_registers(3, outputs, unit=1)
    #Perfect attack scenario attack here - misinformation to master

sys.exit(0)
fig, axis = plt.subplots(figsize=(12,8), nrows = 2, ncols = 3)

axis[0,0] = addPlot(2, 3, 1, plt, secondsPlot, steamStepPlot, "Seconds (s)", "Steam Flow (Kg/s)")
axis[0,1] = addPlot(2, 3, 2, plt, secondsPlot, steamCumulativePlot, "Seconds (s)", "Cumulative Steam Flow (Kg)")
axis[0,2] = addPlot(2, 3, 3, plt, secondsPlot, waterLevelPlot, "Seconds (s)", "Water Level (L)")
axis[1,0] = addPlot(2, 3, 4, plt, secondsPlot, temperaturePlot, "Seconds (s)", "Temperature (C)")
axis[1,1] = addPlot(2, 3, 5, plt, secondsPlot, powerPlot, "Seconds (s)", "Power Out (MW)")
axis[1,2].axis('off')

plt.tight_layout()
plt.show()
