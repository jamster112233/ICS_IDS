import math
import queue
import random
import pygame
import matplotlib.pyplot as plt
import ICSView
import ICSModel
import networkEncoder as ne
from pymodbus3.client.sync import ModbusTcpClient

MODBUS_SLAVE = '192.168.56.102'

ROOM_TEMP = 15
TIME_STEP = 1
TIME_PERIOD = 100000
WATER_LEVEL_INIT = 500000
MEGA = 1000000
HEATER_POWER = 2000 * MEGA
OUT_EXP_POWER = HEATER_POWER * 0.6
DEBUG = False

random.seed(100)

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
ICSView = ICSView.View("HMI", WATER_LEVEL_INIT * 6 / 5)

seconds = 1
power = 0
steamStep = 0
steamCumulative = 0

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

overflowAmount = 0.0
serverSeconds = 0

#Source of physics, not source of what is happening
while seconds < TIME_PERIOD + 2 or done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    #only writing to and reading from slaves
    #get updates from inputs
    #Perfect attack scenario attack here - misinformation from master

    #Add water? do this first then run the fire on it too
    while serverSeconds < seconds:
        result = client.read_holding_registers(0, 21, unit=1)
        addWater = ne.modbusDecode(0, 2, 2, result.registers)
        addFire = ne.modbusDecode(2, 2, 0, result.registers)
        waterLevel = ne.modbusDecode(3, 4, 4, result.registers)
        waterTemp = ne.modbusDecode(7, 2, 2, result.registers)
        powerOut = ne.modbusDecode(9, 6, 2, result.registers)
        steamStep = ne.modbusDecode(13, 2, 4, result.registers)
        powerIn = ne.modbusDecode(16, 6, 2, result.registers)
        serverSeconds = ne.modbusDecode(20, 2, 0, result.registers)

    # REG   3   - 6   = Water Level
    # REG   7   - 8   = Water Temperature
    # REG   9   - 12  = Power Out
    # REG   13  - 15  = Steam Flow
    # REG   16  - 19  = Power In

    ICSModel.addWater(addWater)
    steamCumulative += steamStep
    overflowAmount += max(0, waterLevel + addWater - (WATER_LEVEL_INIT * 6 / 5))

    #DRAW
    ICSView.update(steamStep, steamMax, addWater, waterLevel, powerIn, powerOut, overflowAmount, waterTemp)

    secondsPlot.append(seconds)
    steamStepPlot.append(steamStep)
    steamCumulativePlot.append(steamCumulative)
    waterLevelPlot.append(waterLevel)
    temperaturePlot.append(waterTemp)
    powerPlot.append(powerOut/MEGA)

    if DEBUG:
        print("Sensor values at : ", seconds, "s")
        print("====================================")
        print("Steam OUT   :", steamStep,"kg/s")
        print("Water TEMP  :", waterTemp, "C")
        print("Water LEVEL :", waterLevel, "L")
        print("Power OUT   :", power / MEGA, "MW")
        print("====================================")

    outputs = []

    # Convert and send
    outputs = ne.modbusEncode(0, 2, 0, outputs)
    write = client.write_registers(20, outputs, unit=1)
    client.close()

    #Perfect attack scenario attack here - misinformation to master
    seconds += TIME_STEP

fig, axis = plt.subplots(figsize=(12,8), nrows = 2, ncols = 3)

axis[0,0] = addPlot(2, 3, 1, plt, secondsPlot, steamStepPlot, "Seconds (s)", "Steam Flow (Kg/s)")
axis[0,1] = addPlot(2, 3, 2, plt, secondsPlot, steamCumulativePlot, "Seconds (s)", "Cumulative Steam Flow (Kg)")
axis[0,2] = addPlot(2, 3, 3, plt, secondsPlot, waterLevelPlot, "Seconds (s)", "Water Level (L)")
axis[1,0] = addPlot(2, 3, 4, plt, secondsPlot, temperaturePlot, "Seconds (s)", "Temperature (C)")
axis[1,1] = addPlot(2, 3, 5, plt, secondsPlot, powerPlot, "Seconds (s)", "Power Out (MW)")
axis[1,2].axis('off')

plt.tight_layout()
plt.show()