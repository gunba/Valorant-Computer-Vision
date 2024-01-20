import os
import PIL.Image
import PIL.ImageEnhance
import PIL.ImageOps
import random
import funcs as f

from multiprocessing import Pool

target = 10000

in_dir = 'resources/heroes/'
hero_dir = '../data/agents/'
ult_dir = '../data/ults/'

augs = list()
augs.append(f.brightness)
augs.append(f.saturation)
#augs.append(f.shift)
#augs.append(f.gauss)
#augs.append(f.rotate)
#augs.append(f.resize)
targets = os.listdir(in_dir)

def thread_func(file):
    filepath = in_dir + file
    image = PIL.Image.open(filepath)

    file_noext = file.split('.png')[0]
    file_noslash = file_noext.split(',')
    sub_herodir = hero_dir + file_noslash[0]
    sub_ultdir = ult_dir + file_noslash[1]

    # Make out directory if doesn't exist
    if not os.path.exists(sub_herodir):
        os.makedirs(sub_herodir)

    if not os.path.exists(sub_ultdir):
        os.makedirs(sub_ultdir)

    for x in range(0, target):
        # Create one template with random effects.
        new = f.shift(image, 2)
        new = f.bg(new)

        for y in range(random.randint(0, 2)):
            func = random.choice(augs)
            new = func(new)

        new = new.convert('RGB')
        new.save('%s/%s/%s' % (hero_dir, file_noslash[0], str(x) + 'x' + file_noslash[0] + file_noslash[1] + '.jpg'), "JPEG", quality=random.randint(8, 75))
        new.save('%s/%s/%s' % (ult_dir, file_noslash[1], str(x) + 'x' + file_noslash[0] + file_noslash[1] + '.jpg'), "JPEG", quality=random.randint(8, 75))

if __name__ == '__main__':
    pool = Pool(processes=16)
    pool.map(thread_func, targets)
