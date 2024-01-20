import os
import PIL.Image
import PIL.ImageEnhance
import PIL.ImageOps
import random
import funcs as f

from multiprocessing import Pool

target = 50000

in_dir = 'resources/maps/'
map_dir = '../data/maps/'

augs = list()
augs.append(f.brightness)
augs.append(f.saturation)
targets = os.listdir(in_dir)

def thread_func(file):
    filepath = in_dir + file
    image = PIL.Image.open(filepath)

    file_noext = file.split('.png')[0]
    map_subdir = map_dir + file_noext

    if not os.path.exists(map_subdir):
        os.makedirs(map_subdir)

    for x in range(0, target):
        # Create one template with random effects.
        new = f.shift(image, 20)
        #new = f.rotate(new)
        new = f.shrink(new)
        new = f.bg(new)

        for y in range(random.randint(0, 2)):
            func = random.choice(augs)
            new = func(new)

        new = new.convert('RGB')
        new.save('%s/%s' % (map_subdir, str(x) + '.jpg'), "JPEG", quality=random.randint(8, 75))

if __name__ == '__main__':
    pool = Pool(processes=16)
    pool.map(thread_func, targets)
