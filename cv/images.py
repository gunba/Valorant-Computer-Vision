import glob
import cv2
import os

filenames = glob.glob("images/heroes/*.png")
filenames.sort()

heroes_l = dict()
heroes_r = dict()

for img in filenames:
    name = os.path.basename(img)
    name, _ = os.path.splitext(name)
    heroes_l[name] = cv2.imread(img, 0)
    heroes_r[name] = cv2.flip(heroes_l[name], 1)

filenames = glob.glob("images/guns/*.png")
filenames.sort()

guns = dict()

for img in filenames:
    name = os.path.basename(img)
    name, _ = os.path.splitext(name)
    guns[name] = cv2.imread(img, 0)

filenames = glob.glob("images/mods/*.png")
filenames.sort()

mods = dict()

for img in filenames:
    name = os.path.basename(img)
    name, _ = os.path.splitext(name)
    mods[name] = cv2.imread(img, 0)

def template_match_dict(frame, templates, method=cv2.TM_CCOEFF_NORMED):
    matches = list()
    for k, v in templates.items():
        thr, pos = template_match(frame, v, method)
        matches.append((k, thr, pos))
    return max(matches, key=lambda x: x[1])

def template_match(frame, template, method=cv2.TM_CCOEFF_NORMED):
    # Defense against templates > variable frame inputs (i.e. killfeed)
    if template.shape[1] > frame.shape[1]:
        return 0, (0, 0)

    # Otherwise, go for it.
    res = cv2.matchTemplate(frame, template, method)
    _, min, _, pos = cv2.minMaxLoc(res)
    return min, pos

def avg_color(image, noblack=False):
    b = image[:, :, 0]
    g = image[:, :, 1]
    r = image[:, :, 2]
    if noblack:
        return b[b != 0].mean(), g[g != 0].mean(), r[r != 0].mean()
    else:
        return b.mean(), g.mean(), r.mean()