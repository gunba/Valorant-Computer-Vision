# Objects used to store observations
class Hero:
    def __init__(self):
        self.name = None
        self.ult = -1
        self.state = 'alive'

class Gamedata:
    def __init__(self, tick):
        self.world = None
        self.teams = [list(), list()]
        self.feed = list()
        self.scores = list()
        self.round_num = 0
        self.tick = tick
        self.flip = 0

class Killfeed:
    def __init__(self):
        self.l_hero = None
        self.l_team = None
        self.gun = 'none'
        self.r_hero = None
        self.r_team = None
        self.wallbang = None
        self.headshot = None

# Objects used to store cleaned data
class CookedPickle:
    def __init__(self, rounds, world, winner):
        self.rounds = rounds
        self.world = world
        self.winner = winner




