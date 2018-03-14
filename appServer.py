import queue
import random
import networkEncoder as ne
from pymodbus3.client.sync import ModbusTcpClient

MODBUS_SLAVE = '192.168.56.102'

random.seed(100)
waterLevel = 0

while waterLevel == 0:
    client = ModbusTcpClient(MODBUS_SLAVE)
    result = client.read_holding_registers(3, 13, unit=1)
    waterLevel = ne.modbusDecode(0, 4, 4, result.registers)
    waterTemp = ne.modbusDecode(4, 2, 2, result.registers)
    power = ne.modbusDecode(6, 6, 2, result.registers)
    steamStep = ne.modbusDecode(10, 2, 4, result.registers)

    print(waterLevel)
    print(waterTemp)
    print(power)
    print(steamStep)
    client.close()

#Start the fire
outputs = []
outputs = ne.modbusEncode(1, 2, 0, outputs)
write = client.write_registers(2, outputs, unit=1)

client = ModbusTcpClient(MODBUS_SLAVE)
waterAddQ = queue.Queue()
for i in range(0,10):
    waterAddQ.put(0)

while True:
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
        addWater = ((500000 - waterLevel) * (random.randint(80,120)/100)) + steamStep
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
    print(addWater)

    # Add fire? always
    addFire = 1

    outputs = []
    outputs = ne.modbusEncode(addWater, 2, 2, outputs)
    outputs = ne.modbusEncode(addFire, 2, 0, outputs)
    write = client.write_registers(0, outputs, unit=1)

client.close()