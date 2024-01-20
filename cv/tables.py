# Game object used to store finished product
class Game:
    def __init__(self, world, teams, flip):
        self.world = world
        self.rounds = list()
        self.teams = teams
        self.flip = flip

class Round:
    def __init__(self):
        self.winner = None
        self.events = list()
        self.round_num = 0

class Player:
    def __init__(self, name=None, hero=None, team=None, slot=None):
        self.name = name
        self.hero = hero
        self.team = team
        self.slot = slot

# Events
class Kill:
    def __init__(self, left, weapon, right, headshot, wallbang, time):
        self.left = left
        self.weapon = weapon
        self.right = right
        self.headshot = headshot
        self.wallbang = wallbang
        self.time = time

class Rez:
    def __init__(self, left, right, time):
        self.left = left
        self.right = right
        self.time = time

class Suicide:
    def __init__(self, left, right, time):
        self.left = None
        self.right = None
        self.time = 0

class UltUsed:
    def __init__(self, left, time):
        self.left = left
        self.time = time

class UltGain:
    def __init__(self, left, time):
        self.left = left
        self.time = time
