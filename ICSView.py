import pygame
import math

black = (0,0,0)
white = (255,255,255)
blue = (0,0,255)
grey = (220,220,220)
darkGrey = (150,150,150)
red = (255,0,0)
green = (0,255,0)

MEGA = 1000000

SCREEN_SIZE = (450,850)

TURBINE_CENTRE = (300, 170)
TURBINE_RAD = 120
TURBINE_SPOKES = 10
TURBINE_ROT_RATE = 0.03

BLADE_WIDTH = 2

STEAM_START_Y = 350
STEAM_MAX_LEN = 100

CONTAINER_TL = (150, 360)
CONTAINER_WIDTH = 150
CONTAINER_HEIGHT = 280

WATER_STREAM_SCALER = 14 / 10000

FLAME_PATH = "flame.png"
FLAME_TL = (161, 670)
FLAME_COVER = pygame.Rect(161, 670, 128, 128)

TURBINE_COVER = pygame.Rect(180, 250, 92, 102)
WATER_STREAM = pygame.Rect(118, 333, 65, 612)
WATER_STREAM_COVER = pygame.Rect(118, 333, 65, 309)
POWER_OUT_COVER = pygame.Rect(0, 158, 180, 24)
PIPE_RECT = pygame.Rect(0, 320, 150, 28)

WATER_LABEL_CENTRE = (75, 335)
POWER_OUT_LABEL_CENTRE = (100, 170)
STEAM_LABEL_CENTRE = (225, 300)
POWER_IN_LABEL_CENTRE = (225, 755)

class View:
    def __init__(self, title, containerOverflow):
        pygame.init()
        pygame.display.set_caption(title)
        self.window = pygame.display.set_mode(SCREEN_SIZE, pygame.DOUBLEBUF)
        self.screen = pygame.display.get_surface()
        self.turbine = Turbine(TURBINE_SPOKES, TURBINE_CENTRE, TURBINE_RAD, black)
        self.flame = pygame.image.load(FLAME_PATH)
        self.container = ContainerGraphics(CONTAINER_TL, CONTAINER_WIDTH, CONTAINER_HEIGHT, containerOverflow)

    def update(self, steamStep, steamMax, addWater, waterLevel, powerIn, powerOut, overflowAmount, temperature):
        pygame.draw.rect(self.screen, black, FLAME_COVER)

        if powerIn / MEGA > 0.01:
            self.screen.blit(self.flame, FLAME_TL)
            textBlit(self.screen, [powerIn / MEGA], [1], ["MW"], POWER_IN_LABEL_CENTRE, 24, black)

        pygame.draw.rect(self.screen, black, WATER_STREAM_COVER)
        self.container.drawAll(self.screen, waterLevel, overflowAmount, temperature)

        pygame.draw.rect(self.screen, darkGrey, PIPE_RECT)

        if addWater > 0:
            pygame.draw.arc(self.screen, blue, WATER_STREAM, 0, math.pi * 0.5,
                            int(addWater * WATER_STREAM_SCALER) + 1)

        pygame.draw.rect(self.screen, black, POWER_OUT_COVER)

        self.turbine.draw(self.screen, TURBINE_ROT_RATE * (steamStep / steamMax))

        if steamStep > steamMax * 0.005:
            steamLen = steamStep * STEAM_MAX_LEN / steamMax
            for i in range(1, 5):
                pygame.draw.line(self.screen, grey, (150 + i * 30, STEAM_START_Y), (150 + i * 30, STEAM_START_Y - steamLen), 2)

        textBlit(self.screen, [addWater], [2], ["L/s"], WATER_LABEL_CENTRE, 24, black)
        textBlit(self.screen, [powerOut / MEGA], [2], ["MW"], POWER_OUT_LABEL_CENTRE, 24)
        textBlit(self.screen, [steamStep], [2], ["Kg/s"], STEAM_LABEL_CENTRE, 24)
        pygame.display.flip()

class ContainerGraphics():
    def __init__(self, coordTopLeft, width, height, containerOverflow):
        self.coordTopLeft = coordTopLeft
        self.height = height
        self.width = width
        self.pixPerLitre = height / containerOverflow
        self.lastOverflow = 0.0

    def drawAll(self, screen, waterLevel, overflowAmount, temperature):
        self.drawWater(screen, waterLevel, overflowAmount, temperature)

    def drawContainer(self, screen):
        pygame.draw.lines(screen, white, False, ((self.coordTopLeft),
                                                 (self.coordTopLeft[0], self.coordTopLeft[1] + self.height),
                                                 (self.coordTopLeft[0] + self.width, self.coordTopLeft[1] + self.height),
                                                 (self.coordTopLeft[0] + self.width, self.coordTopLeft[1])), 2)

    def drawWater(self, screen, waterLevel, overflowAmount, temperature):
        pygame.draw.rect(screen, black, pygame.Rect(0, self.coordTopLeft[1] - 2, self.width * 3, self.height + 4))

        pxWaterLevel = math.floor(self.coordTopLeft[1] + self.height - (waterLevel * self.pixPerLitre))
        textCol = white

        if(self.coordTopLeft[1] + self.height - pxWaterLevel > 0):
            pygame.draw.rect(screen, blue, pygame.Rect(self.coordTopLeft[0] + 2,
                                                   pxWaterLevel, self.width - 2, self.coordTopLeft[1] + self.height - pxWaterLevel))
            #Still overflowing!
            if(self.lastOverflow < overflowAmount):
                self.lastOverflow = overflowAmount
                textCol = red
                pygame.draw.rect(screen, blue, pygame.Rect(self.coordTopLeft[0] - 2, pxWaterLevel - 2, self.width + 6,
                                                                     self.coordTopLeft[1] + self.height - pxWaterLevel + 4))

        pxOverflowLevel = math.floor(self.coordTopLeft[1] + self.height - (overflowAmount * self.pixPerLitre * 0.5)) + 2
        pxBottom = self.coordTopLeft[1] + self.height + 2
        if pxBottom > pxOverflowLevel:
            pygame.draw.rect(screen, blue, pygame.Rect(0, pxOverflowLevel, self.width, pxBottom - pxOverflowLevel))
            pygame.draw.rect(screen, blue, pygame.Rect(2 * self.width, pxOverflowLevel, self.width, pxBottom - pxOverflowLevel))
            textBlit(screen, [overflowAmount], [1], ["L"], (math.floor(self.width / 2),
                                                                    self.coordTopLeft[1] + math.floor(self.height / 2)), 24)
        self.drawContainer(screen)
        textBlit(screen, [waterLevel, temperature], [1, 1], ["L", "C"], (self.coordTopLeft[0] + math.floor(self.width / 2),
                                                       self.coordTopLeft[1] + math.floor(self.height / 2)), 24, textCol)

class Blade:
    def __init__(self, offset, colour, centre, length):
        self.offset = offset
        self.colour = colour
        self.centre = centre
        self.length = length

    def draw(self, screen, iterator):
        radPos = (iterator + self.offset)
        xEnd = self.centre[0] + (self.length * math.cos(radPos))
        yEnd = self.centre[1] + (self.length * math.sin(radPos))
        pygame.draw.line(screen, self.colour, self.centre, (xEnd, yEnd), BLADE_WIDTH)

class Turbine:
    bladeColour = white

    def __init__(self, numBlades, centre, radius, backColour):
        self.numBlades = numBlades
        self.allBlades = []
        self.centre = centre
        self.backColour = backColour
        self.radius = radius
        self.iterator = 0.0

        radIncrement = 2 * math.pi/numBlades

        for x in range(0, numBlades):
            self.allBlades.append(Blade(x * radIncrement, self.bladeColour, self.centre, radius))

    def draw(self, screen, increment):
        self.iterator += increment
        pygame.draw.rect(screen, self.backColour, pygame.Rect(self.centre[0] - self.radius - 10,
                                                              self.centre[1] - self.radius - 10,
                                                              self.centre[0] + self.radius + 10,
                                                              self.centre[1] + self.radius + 10))
        pygame.draw.rect(screen, black, TURBINE_COVER)
        for blade in self.allBlades:
            blade.draw(screen, self.iterator)

def textBlit(screen, values, rounding, units, centre, size, colour=white):
    basicfont = pygame.font.SysFont(None, size)
    numVals = len(values)
    text = []

    for i in range(0, numVals):
        text.append(str(round(values[i], rounding[i])) + units[i])
        textBlit = basicfont.render(text[i], True, colour)
        textrect = textBlit.get_rect()
        textrect.centerx = centre[0]
        textrect.centery = centre[1] - (size * ((0.5 * numVals) + (-0.5 - i)))
        screen.blit(textBlit, textrect)
