import os
import PIL.Image
import PIL.ImageEnhance
import PIL.ImageOps
import random
import funcs as f

from multiprocessing import Pool

target = 20000

in_dir = 'resources/scores/'
_dir = '../data/scores/'

augs = list()
augs.append(f.brightness)
augs.append(f.saturation)
targets = os.listdir(in_dir)

def thread_func(file):
    filepath = in_dir + file
    image = PIL.Image.open(filepath)

    file_noext = file.split('.png')[0]
    _subdir = _dir + file_noext

    if not os.path.exists(_subdir):
        os.makedirs(_subdir)

    for x in range(0, target):
        # Create one template with random effects.
        new = f.shift(image, 3)
        new = f.bg(new)

        for y in range(random.randint(0, 2)):
            func = random.choice(augs)
            new = func(new)

        new = new.convert('RGB')
        new.save('%s/%s' % (_subdir, str(x) + '.jpg'), "JPEG", quality=random.randint(8, 75))

if __name__ == '__main__':
    pool = Pool(processes=16)
    pool.map(thread_func, targets)
