import math
import queue
import random

ROOM_TEMP = 15

WATER_LEVEL_INIT = 500000
WATER_SHC = 4181
WATER_LHC = 2258000
WATER_BOIL_C = 100

MEGA = 1000000
HEATER_POWER = 2000 * MEGA
OUT_EXP_POWER = HEATER_POWER * 0.6

FLUID_LAYER_INIT = 500

class Model:
    def __init__(self, containerOverflow):
        self.container = Container(ROOM_TEMP, FLUID_LAYER_INIT, WATER_LEVEL_INIT, containerOverflow)

    def addHeat(self, joules):
        return self.getContainer().addHeat(joules)

    def loseHeat(self):
        return self.getContainer().loseHeat()

    def addWater(self, volume):
        return self.getContainer().addWater(volume)

    def getContainer(self):
        return self.container


class Container:
    def __init__(self, initTemp, initLayers, startLitres, containerOverflow):
        self.currentTemp = initTemp
        self.layerVolume = startLitres / initLayers
        self.maxLayers = initLayers
        self.fluidLayers = queue.Queue()
        self.waterLevel = startLitres
        self.evaporationCarry = 0
        self.containerOverflow = containerOverflow
        self.overflowAmount = 0.0

        for i in range(0, self.maxLayers):
            self.fluidLayers.put(FluidLayer(self.currentTemp, self.layerVolume))

    def addWater(self, volume):
        tempLevel = self.waterLevel + volume

        overflow = 0
        if tempLevel > self.containerOverflow:
            overflow = tempLevel - self.containerOverflow

        addVol = volume - overflow

        if addVol > 0:
            self.fluidLayers.put(FluidLayer(ROOM_TEMP, addVol))

        self.overflowAmount += overflow
        self.waterLevel += addVol

    def addHeat(self, joules):
        tempFluidLayers = queue.Queue()
        cumulativeSteamMass = 0.0
        currentTemperature = 0.0

        numLayers = self.fluidLayers.qsize()
        evaporationStatus = self.evaporationCarry
        runningVol = self.waterLevel

        for i in range(1, numLayers + 1):
            element = self.fluidLayers.get()
            currentVol = runningVol - element.getVolume()
            evaporationStatus, steamMass = element.addHeat((joules * self.determineWeight(currentVol, runningVol, self.waterLevel)) + evaporationStatus)
            runningVol = currentVol
            cumulativeSteamMass += steamMass

            if evaporationStatus == 0:
                tempFluidLayers.put(element)
                currentTemperature += (element.getTemperature() * element.getVolume())

        self.fluidLayers = tempFluidLayers
        self.waterLevel -= cumulativeSteamMass
        self.waterLevel = math.fabs(self.waterLevel)

        if self.fluidLayers.qsize() == 0 :
            self.currentTemp = ROOM_TEMP
        else:
            currentTemperature /= self.waterLevel

            if currentTemperature < ROOM_TEMP:
                print("TEMP ERROR", self.fluidLayers.qsize(), "x", currentTemperature)

            self.currentTemp = currentTemperature

        self.evaporationCarry = evaporationStatus
        return cumulativeSteamMass

    def loseHeat(self):
        tempFluidLayers = queue.Queue()
        currentTemperature = 0.0

        numLayers = self.fluidLayers.qsize()
        evaporationStatus = self.evaporationCarry

        for i in range(1, numLayers + 1):
            element = self.fluidLayers.get()
            newTemp = element.takeHeat()

            if evaporationStatus == 0:
                tempFluidLayers.put(element)
                currentTemperature += (newTemp * element.getVolume())

        self.fluidLayers = tempFluidLayers

        return 0

    def determineWeight(self, last, num, dist):
        return ((num ** 2) - (last ** 2)) / (dist ** 2)

    def getCurrentTemp(self):
        return self.currentTemp

    def getWaterLevel(self):
        return self.waterLevel

    def getOverflowAmount(self):
        return self.overflowAmount

    def drawAll(self):
        self.cg.drawAll()

    def drawFast(self):
        self.cg.drawWater()


class FluidLayer:
    def __init__(self, temp, layerVolume):
        self.temp = temp
        self.lhcProgress = WATER_LHC * layerVolume

    def addHeat(self, joules):
        prevLhcProgress = self.lhcProgress

        if self.temp < WATER_BOIL_C:
            self.temp += joules / (WATER_SHC * self.getVolume())
            if self.temp >= WATER_BOIL_C:
                self.lhcProgress -= (self.temp - WATER_BOIL_C) * (WATER_SHC * self.getVolume())
                self.temp = WATER_BOIL_C
        else:
            self.lhcProgress -= joules

        #0 is complete
        excessEnergy = 0
        if self.lhcProgress < 0:
            excessEnergy = self.lhcProgress * -1
            steamMass = prevLhcProgress / WATER_LHC
        else:
            steamMass = (prevLhcProgress - self.lhcProgress) / WATER_LHC

        return excessEnergy, steamMass

    def takeHeat(self):
        if self.temp > ROOM_TEMP:
            self.temp *= (0.98 * (random.randint(95, 105) / 100))

        if self.temp < ROOM_TEMP:
            self.temp = ROOM_TEMP

        return self.temp

    def getVolume(self):
        return self.lhcProgress / WATER_LHC

    def getTemperature(self):
        return self.temp
