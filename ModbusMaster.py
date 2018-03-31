import Queue as queue
import random
import NetworkEncoder as ne
from pymodbus.client.sync import ModbusTcpClient

MODBUS_SLAVE = 'ms.ics.example.com'

waterLevel = 0

while waterLevel == 0:
    client = ModbusTcpClient(MODBUS_SLAVE)
    result = client.read_holding_registers(3, 13, unit=1)
    waterLevel = ne.modbusDecode(0, 4, 4, result.registers)
    waterTemp = ne.modbusDecode(4, 2, 2, result.registers)
    power = ne.modbusDecode(6, 6, 2, result.registers)
    steamStep = ne.modbusDecode(10, 2, 4, result.registers)
    client.close()

#Start the fire
outputs = []
outputs = ne.modbusEncode(1, 2, 0, outputs)
write = client.write_registers(2, outputs, unit=1)

client = ModbusTcpClient(MODBUS_SLAVE)
waterAddQ = queue.Queue()
for i in range(0,10):
    waterAddQ.put(0)

backoffFlag = True
backoff = random.randint(1, 7000)
serverSeconds = 0
while serverSeconds < 7200:
    #Read values from slave
    result = client.read_holding_registers(0, 21, unit=1)
    addWater = ne.modbusDecode(0, 2, 2, result.registers)
    addFire = ne.modbusDecode(2, 2, 0, result.registers)
    waterLevel = ne.modbusDecode(3, 4, 4, result.registers)
    waterTemp = ne.modbusDecode(7, 2, 2, result.registers)
    powerOut = ne.modbusDecode(9, 6, 2, result.registers)
    steamStep = ne.modbusDecode(13, 2, 4, result.registers)
    powerIn = ne.modbusDecode(16, 6, 2, result.registers)
    serverSeconds = ne.modbusDecode(20, 2, 0, result.registers)

    #Determine pump action based on water level, and add a random 'noise' factor
    if waterLevel < 500000:
        addWater = ((500000 - waterLevel) * (float(random.randint(80,120))/100)) + steamStep
    else:
        addWater = steamStep * 3 / 4

    addWater = min(addWater, 10000)
    waterAddQ.get()
    waterAddQ.put(addWater)
    runningWaterAdd = 0.0
    waterAddQ2 = queue.Queue()
    while waterAddQ.qsize() > 0:
        addVal = waterAddQ.get()
        runningWaterAdd += addVal
        waterAddQ2.put(addVal)

    waterAddQ = waterAddQ2
    addWater = runningWaterAdd / waterAddQ.qsize()

    # Add fire? always
    addFire = 1
    # Initiate backoff
    if waterLevel >= 600000:
        backoffFlag = True
    elif waterLevel <= 505000 and backoff <= 0:
        backoffFlag = False
        backoff = random.randint(1, 1000)
    elif waterLevel <= 505000:
        backoff -= 1

    if not backoffFlag:
        addFire = 2

    outputs = []
    outputs = ne.modbusEncode(addWater, 2, 2, outputs)
    outputs = ne.modbusEncode(addFire, 2, 0, outputs)
    print(backoff)
    print(outputs)
    write = client.write_registers(0, outputs, unit=1)

client.close()
