import numpy as np
import cv2
import models as mdl
import images as i
from objects import *
import time
from timeit import timeit
import funcs as f

#### This step is used to get the initial frame data from a video and pickle it (raw) using CV/ML.
@timeit
def process_round(video, flip=1):
    capture = cv2.VideoCapture(video)
    prev_heroes = list()
    data = list()
    ticks = 0

    while True:
        grab = capture.grab()
        if grab:
            msec = capture.get(cv2.CAP_PROP_POS_MSEC) / 1000
            if msec >= ticks:

                # Capture every Xth frame based on tickrate.
                timer = time.time()
                _, frame = capture.retrieve()

                # Resize incase of 720p
                frame = cv2.resize(frame, (1920, 1080), cv2.INTER_CUBIC)

                # Instantiate game data for this frame.
                gd = Gamedata(ticks)
                gd.flip = 1 if flip else 0

                # Get map
                world = frame[20:488, 28:496]
                world = np.reshape(world, [1, 468, 468, 3])
                gd.world = mdl.predict('maps', world)[0]

                # Get score frames & predict (1 - Normal, 2 - Bugged UI)
                scores = [frame[39:64, 806:842], frame[38:63, 1081:1117]]

                for score in scores:
                    rs = np.reshape(score, [1, 25, 36, 3])
                    gd.scores.append(mdl.predict('scores', rs)[0])

                # Get killfeed frames and partition
                lines = list()
                for x in range(0, 5):
                    # Cut the max potential line width
                    line = frame[99+(x*38):136+(x*38), 1410:1885]

                    # We create a left and right killfeed search area (for the 2 icons per line)
                    lhero = cv2.cvtColor(line[0:line.shape[0], 0:line.shape[1]-172], cv2.COLOR_BGR2GRAY)
                    rhero = cv2.cvtColor(line[0:line.shape[0], 361:line.shape[1]], cv2.COLOR_BGR2GRAY)
                    lines.append((line, lhero, rhero))

                # Process killfeed (traditional CV)
                index = 0
                if len(prev_heroes) > 0:
                    for y in lines:
                        # Search for right hero out of heroes seen in previous hero bar read
                        r_hero, r_thresh, r_pos = i.template_match_dict(y[2], {k: v for k, v in i.heroes_r.items() if k in prev_heroes})
                        if r_thresh > 0.65:
                            # And now for the left hero (we require lower thresh since we must already have seen right hero)
                            l_hero, l_thresh, l_pos = i.template_match_dict(y[1], {k: v for k, v in i.heroes_l.items() if k in prev_heroes})
                            if l_thresh > 0.60:
                                # Valid killfeed entry.
                                kf = Killfeed()
                                kf.l_hero = l_hero
                                kf.r_hero = r_hero

                                # Cut down to exact line
                                line = y[0][0:y[0].shape[0], l_pos[0]:(r_pos[0]+387)]

                                #Get team colors (if green > red at specific point)
                                def get_team_colors(frame):
                                    b, g, r = i.avg_color(frame)
                                    # cv_error(frame, 'b%s.g%s.r%s.t%s' % (round(b), round(g), round(r), ticks))
                                    return 0 if g > r else 1

                                # Use width of killfeed line to approximate center (f(x) = y)
                                h, w, _ = line.shape
                                y = int((0.80707*w) - 34.54758)

                                # We want a 20*20px block. Killfeed color blocks.
                                kf.l_team = get_team_colors(line[4:(h-4), (y-50):(y-30)])
                                kf.r_team = get_team_colors(line[4:(h-4), (y+25):(y+45)])

                                #cv_error(line, 'L%s.LH%s.R%s.RH%s.I%s.T%s' % (kf.l_team, kf.l_hero, kf.r_team, kf.r_hero, index, ticks))

                                # Now we look for gun/mods @ 0.2-0.8
                                line = cv2.cvtColor(line[0:line.shape[0], int(0.2*line.shape[1]):int(0.8*line.shape[1])], cv2.COLOR_BGR2GRAY)

                                # Match for artificial gun templates (cv)
                                g_gun, g_thresh, g_pos = i.template_match_dict(line, i.guns)

                                # Pretty trusting (sometimes classics appear as unknown)
                                kf.gun = g_gun if g_thresh > 0.50 else 'unknown'

                                # Headshots and wallbangs (hoping for the best)
                                w_thresh, _ = i.template_match(line, i.mods['wallbang'])
                                h_thresh, _ = i.template_match(line, i.mods['headshot'])

                                # Default thresh for headshots/wallbangs
                                kf.headshot = 1 if h_thresh > 0.75 else 0
                                kf.wallbang = 1 if w_thresh > 0.75 else 0

                                # Append finished killfeed
                                gd.feed.append(kf)
                        index += 1

                fhero = dict()
                fhero[0] = [12, 75, 438, 494]
                fhero[1] = [12, 75, 1163, 1219]

                # For both teams
                for t in range(0, 2):
                    # For all hero slots
                    for p in range(0, 5):
                        hero = Hero()

                        # Get the hero frame and reshape for ML
                        hf = frame[fhero[t][0]:fhero[t][1], (fhero[t][2]+(66*p)):(fhero[t][3]+(66*p))]
                        hfr = np.reshape(hf, [1, 63, 56, 3])

                        # We have 2 models that use same size input
                        _hero = mdl.predict('agents', hfr)[0]
                        _ult = mdl.predict('ults', hfr)[0]

                        # Lets convert ultstate 2 to 0 for now (they are currently using ult)
                        if _ult == 2:
                            _ult = 0

                        hero.name = _hero
                        hero.ult = _ult

                        gd.teams[t].append(hero)

                # List confirmed heroes for killfeed scanning in next cycle
                prev_heroes = [x.name for x in gd.teams[0] + gd.teams[1] if x.name != 'dead']

                # Debug output of herobar/killfeed
                debug = gd.world + ',' + gd.teams[0][0].name + ',' + gd.teams[0][1].name + ',' + gd.teams[0][2].name + ',' + gd.teams[0][3].name + ',' + gd.teams[0][4].name
                debug += ',' + gd.teams[1][0].name + ',' + gd.teams[1][1].name + ',' + gd.teams[1][2].name + ',' + gd.teams[1][3].name + ',' + gd.teams[1][4].name + ': ' + str(time.time()-timer) + ' - '

                for x in gd.feed:
                    debug += '[%s %s >%s> %s %s]' % (x.l_team, x.l_hero, x.gun, x.r_team, x.r_hero)

                debug += ' (%s to %s)' % (gd.scores[0], gd.scores[1])

                ticks += 1

                print(debug)

                data.append(gd)
        else:
            f.save_object(data, 'pickles/raw/' + video.split('.')[0])
            break

def cv_error(image, name, folder="debug"):
    print(folder + '/' + str(name) + ".jpg")
    cv2.imwrite(folder + '/' + str(name) + ".jpg", image)
    return None
    
#process_round('1.mp4')
process_round('2.mp4')
#process_round('3.mp4')
#process_round('4.mp4')
#process_round('5.mp4')
#process_round('6.mp4')
#process_round('7.mp4')
#process_round('8.mp4')
#process_round('9.mp4')
#process_round('10.mp4')