from planet import Planet

class Player(object):

    def __init__(self, nome):
        self.name = nome;
        self.planets = []
        self.allCords = []

    def getAllCords(self):
        return self.allCords

    def getPlanets(self):
        return self.planets

    def getName(self):
        return self.self.name

    def addPlanet(self, planet):
        self.planets.append(planet)
        self.allCords.append(planet.coords)
