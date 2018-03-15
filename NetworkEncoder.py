import math
#Inputs
#REG    0   - 1   = Water add vol
#REG    2         = Power in (0 or 1)
# 3 REGs

# Outputs
# REG   3   - 6   = Water Level
# REG   7   - 8   = Water Temperature
# REG   9   - 12  = Power Out
# REG   13  - 15  = Steam Flow
# REG   16  - 19  = Power In
# REG   20  = Seconds
# 19 REGs

# 22 REGs = 44 bytes
#get18     0  1      2  3  4   5  6   7  8  9 10 11 12 13 14 15 16 17 18
#get22     0  1  2  3  4      5  6  7   8  9  10 11 12 13 14 15 16 17 18 19 20 21
#         [0, 0, 0, 7, 41248, 0, 0, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]

def modbusEncode(baseVal, bytesInt, bytesReal, outArr):
    if bytesInt % 2 != 0 or bytesReal % 2 != 0:
        return 0
    
    intRunner = int(math.floor(baseVal))

    if len(outArr) != 0:
        index = len(outArr)
    else:
        index = 0

    for i in range(bytesInt - 2, -1, -2):
        outArr.append(intRunner >> (i * 8))
        intRunner -= (outArr[index] << (i * 8))
        index += 1
    
    realRunner = baseVal - math.floor(baseVal)
    realRunner *= (2 ** (bytesReal * 8))
    realRunner = int(math.floor(realRunner))
    
    for i in range(bytesReal - 2, -1, -2):
        outArr.append(realRunner >> (i * 8))
        realRunner -= (outArr[index] << (i * 8))
        index += 1
    
    return outArr

def modbusDecode(startIndex, bytesInt, bytesReal, inArr):
    if bytesInt % 2 != 0 or bytesReal % 2 != 0:
        return 0
    
    value = 0
    index = startIndex
    
    for i in range(bytesInt - 2, -1, -2):
        value += inArr[index] << (i * 8)
        index += 1
    
    for i in range(bytesReal - 2, -1, -2):
        value += (inArr[index] << (i * 8))/(2 ** (bytesReal * 8))
        index += 1
    
    return value

