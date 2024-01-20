#### This step interprets the finished data product into actual gameplay insights and creates objects that can be stored.
import glob
import funcs as f
from tables import *

filenames = glob.glob("pickles/cooked/*")

for pickle in filenames:
    json = f.load_object(pickle)

    teams = [[], []]
    init = json.rounds[0][0].teams
    for t in range(0, 2):
        for h in range(0, 5):
            teams[t].append(Player(name="%s_%s" % (init[t][h].name, t), hero=init[t][h].name, team=t, slot=h))

    # Grab the flip state from the first frame
    fl = json.rounds[0][0].flip

    # Create our primary game record with sub records of teams+rounds.
    game = Game(world=json.world, teams=teams, flip=fl)

    # Iterate through rounds
    for i, round in enumerate(json.rounds):
        r = Round()

        # Calculate winner from next or last round (init defender left)
        c = round[0]
        _c = [c.scores[1], c.scores[0]] if sum(c.scores) >= 12 and fl else [c.scores[0], c.scores[1]]
        # If it's the last round, check if one team had more points already (they must have won for game to end)
        # Else we take the team with more 13 points (will break in cases of 6-6 half resets but whatever)
        if i+1 == len(json.rounds):
            if _c[0] > _c[1]:
                r.winner = 0
            elif _c[0] < _c[1]:
                r.winner = 1
            else:
                r.winner = json.winner
        # It's not last round - who's score increased?
        else:
            n = json.rounds[i+1][0]
            _n = [n.scores[1], n.scores[0]] if sum(n.scores) >= 12 and fl else [n.scores[0], n.scores[1]]
            if _c[0] < _n[0]:
                r.winner = 0
            else:
                r.winner = 1

        # Outside frame tracker (per round)
        prev = None
        deaths = list()
        rezzes = list()

        for j, frame in enumerate(round):
            # First round in rounds
            r.round_num = frame.round_num

            if j > 15:
                # We need to know if the top bars have flipped (swapped sides)
                flip = [1, 0] if r.round_num > 12 and fl else [0, 1]

                if prev is None:
                    prev = frame
                else:
                    for t in range(0, 2):
                        for h in range(0, 5):
                            # if frame.teams[t][h].ult in (1, 2) and prev.teams[t][h].ult == 0:
                            #     # Ult was gained at this step.
                            #     #r.events.append(UltGain(left=game.teams[t][h], time=j))
                            if frame.teams[t][h].ult == 0 and prev.teams[t][h].ult in (1, 2):
                                # Ult was used at this step.
                                r.events.append(UltUsed(left=game.teams[t][h], time=j))

                prev = frame

                # Hack to prevent rollover kills from prev round being double counted. There is always buy time.
                for line in frame.feed:
                    left = next((x for x in game.teams[flip[line.l_team]] if x.hero == line.l_hero), None)
                    right = next((x for x in game.teams[flip[line.r_team]] if x.hero == line.r_hero), None)
                    if left and right:
                        if line.l_hero == 'sage' and line.l_team == line.r_team and right not in rezzes:
                            # This is a res.
                            # Make sure we have the respective kill (prevent false positives)
                            if right in deaths:
                                deaths.remove(right)
                                r.events.append(Rez(left=left, right=right, time=j))
                                rezzes.append(right)
                        elif line.l_team != line.r_team and right not in deaths:
                            # This is a kill.
                            r.events.append(Kill(left=left, weapon=line.gun, right=right, headshot=line.headshot, wallbang=line.wallbang, time=j))
                            deaths.append(right)
                        elif line.l_hero == line.r_hero and line.l_team == line.r_team and right not in deaths:
                            # Suicide
                            r.events.append(Suicide(left=left, right=right, time=j))
        game.rounds.append(r)

    filename = pickle.split('\\')[-1]
    f.save_object(game, 'pickles/diced/' + filename)

