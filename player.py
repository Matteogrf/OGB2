from planet import Planet
from excelManager import ExcelManager

class Player(object):

    def __init__(self, nome):
        self.name = nome;
        self.planets = []
        self.allCords = []
        self.excel = ExcelManager(nome)

    def getAllCords(self):
        return self.allCords

    def getPlanets(self):
        return self.planets

    def getName(self):
        return self.self.name

    def addPlanet(self, planet):
        self.planets.append(planet)
        self.allCords.append(planet.coords)

    def logAttivita(self, coordinate, isMoon, time):
        self.excel.write_time(coordinate, isMoon, time)
