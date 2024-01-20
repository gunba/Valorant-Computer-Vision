#### This step is used to cleanup data received from initiator (i.e. vision step) by using smoothing and removing impossible data.
import funcs as f
from objects import *
import glob

def cook_pickle(pickle):
    json = f.load_object(pickle)

    # A powerful smoothing function.
    def roll_dough(l, n=4):
        _list = list()
        for i, _ in enumerate(l):
            _set = list()
            for j in range(i-n, i+n):
                if 0 <= j < len(l):
                    _set.append(l[j])
            mode = max(set(_set), key=_set.count)
            _list.append(mode)
        return _list

    # Get and intify all score values (enumerate in later)
    scores = list()

    scores.append([int(x.scores[0]) for x in json])
    scores.append([int(x.scores[1]) for x in json])

    # Average the world
    world = [x.world for x in json]
    world = max(set(world), key=world.count)

    # Grab the winner now before we annihilate it
    l13 = [x for x in scores[0][-20:] if x == 13]
    r13 = [x for x in scores[1][-20:] if x == 13]

    # Calculate the winner by who has more 13 scores
    winner = 1 if l13 > r13 else 0

    # Aggressively smooth score. May need more smoothing.
    scores[0] = roll_dough(scores[0], n=45)
    scores[1] = roll_dough(scores[1], n=45)

    # Clean up scores from dough rolling (losing 13 round data in progress)
    for i, gd in enumerate(json):
        gd.scores = (scores[0][i], scores[1][i])
        gd.round_num = (gd.scores[0]+gd.scores[1])+1

    # Max rounds is 26 i.e. we only need to check 1-26
    # found_start ensures that we find the first round (if missing first few)
    rounds = list()
    for i in range(1, 26):
        slices = [x for x in json if x.round_num == i]
        if len(slices) > 0:
            rounds.append(slices)

    # Append 10 or so frames from the start of each round to the end of the previous round
    # This is because the score updates before the round cycles
    _rounds = list()
    for i, round in enumerate(rounds):
        if i == 0:
            # If it's the first round
            _rounds.append(round+rounds[i+1][-10:])
        elif i == len(rounds)-1:
            # If it's the last round
            _rounds.append(round[10:])
        else:
            # This round is in the middle
            _rounds.append(round[10:]+rounds[i+1][-10:])
    rounds = _rounds

    rounds = [x for x in rounds if len(x) > 30]

    #However this code will allow 12-4 and 8-8 e.g. to be grouped so replace outliers.
    for round in rounds:
        s = [x.scores for x in round]
        actual = max(set(s), key=s.count)
        for frame in round:
            frame.scores = actual
            frame.round_num = (sum(actual)+1)

    # Clean up compositional data (comp can't change)
    comps = [list(), list()]
    for round in rounds:
        for i, gd in enumerate(round):
            if gd.round_num <= 12:
                for x in range(0, 2):
                    num = [x for x in gd.teams[x] if x.name == 'dead']
                    if len(num) == 0:
                        comps[x].append(','.join([x.name for x in gd.teams[x]]))

    comps = [max(set(comps[0]), key=comps[0].count).split(','),
             max(set(comps[1]), key=comps[1].count).split(',')]

    # We use this function to replace/reorganize heroes in a comp.
    def rebuild_comp(data, comp):
        heroes = list()
        for h in comp:
            hero = next((y for y in data if y.name == h), None)
            if not hero:
                hero = Hero()
                hero.name = h
                hero.state = 'dead'
            heroes.append(hero)
        return heroes

    # We know for sure the comp and the order. Now replace all hero data with new data.
    for round in rounds:
        for gd in round:
            for x in range(0, 2):
                gd.teams[x] = rebuild_comp(gd.teams[x], comps[x])

    # Function to replace 'dead' ults with previous data after tracking.
    # Also converts all ults to int since we don't do that anywhere else.
    # Model technically returns strings so
    def replace_ults(ults):
        last = -1
        new_ults = list()
        for u in ults:
            # If this player is not dead..
            uint = int(u)
            if uint >= 0:
                last = uint
            new_ults.append(last)
        return new_ults

    # Finally we just need to cleanup the hero/ult data (i.e. avoid alive/dead/alive, ult/none/ult)
    for round in rounds:
        for y in range(0, 2):
            for x in range(0, 5):
                state = list()
                ults = list()

                for gd in round:
                    state.append(gd.teams[y][x].state)
                    ults.append(gd.teams[y][x].ult)

                state = roll_dough(state, 3)
                ults = roll_dough(ults, 10)
                ults = replace_ults(ults)

                for i, gd in enumerate(round):
                    gd.teams[y][x].state = state[i]
                    gd.teams[y][x].ult = ults[i]

    # Filter out any garbage with 0 len
    rounds = [x for x in rounds if len(x) > 0]

    return CookedPickle(rounds, world, winner)

filenames = glob.glob("pickles/raw/*")

for pickle in filenames:
    game = cook_pickle(pickle)
    raw = pickle.split('\\')[-1]
    raw = raw.split('/')[-1]
    f.save_object(game, 'pickles/cooked/' + raw)




