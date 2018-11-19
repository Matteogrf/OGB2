from planet import Planet

class Player(object):

    def __init__(self, nome):
        self.name = nome;
        self.planets = []

    def getPlanets(self):
        return self.planets

    def getName(self):
        return self.self.name

    def addPlanet(self, planet):
        self.planets.append(planet)
