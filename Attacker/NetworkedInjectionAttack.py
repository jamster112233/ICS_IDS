import random
import time
import NetworkEncoder as ne
from pymodbus.client.sync import ModbusTcpClient

MODBUS_SLAVE = 'ms.ics.example.com'
client = ModbusTcpClient(MODBUS_SLAVE)

outputs = []
outputs = ne.modbusEncode(0, 4, 4, outputs)
outputs = ne.modbusEncode(0, 2, 2, outputs)
outputs = ne.modbusEncode(0, 6, 2, outputs)
outputs = ne.modbusEncode(0, 2, 4, outputs)
outputs = ne.modbusEncode(0, 6, 2, outputs)
outputs = ne.modbusEncode(0, 2, 0, outputs)
write = client.write_registers(3, outputs, unit=1)
client.close()
client = ModbusTcpClient(MODBUS_SLAVE)
backOff = random.randint(0,50)

