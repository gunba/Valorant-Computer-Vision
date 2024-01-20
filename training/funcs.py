import random
import os
from PIL import ImageFilter, Image, ImageEnhance

# We need a few functions for augmentation
# Blur random
# Resize and resize again random
# Brightness shift +-

def gauss(image):
    return image.filter(ImageFilter.GaussianBlur(round(random.uniform(1, 2), 2)))

def shrink(image):
    # First we create a shrunk version of the original
    i = round(random.uniform(1, 2), 2)
    w, h = image.size
    nw = int(w/i)
    nh = int(w/i)
    image = image.resize((nw, nh), 1)

    # Then we create a new template to overlay it into
    templ = Image.new('RGBA', (w, h))

    l = int(w/2)-int(nw/2)
    u = int(h/2)-int(nh/2)

    # Paste it using some basic math
    templ.paste(image, (l, u))
    return templ

def bg(image):
    # Select a background randomly
    dir = 'backgrounds/'
    file = random.choice(os.listdir(dir))
    filepath = dir+file
    bg = Image.open(filepath)

    # Get size of input and bg
    iw, ih = image.size
    bw, bh = bg.size

    # We want a random cutout from BG at I size
    left = random.randint(0, bw-iw)
    upper = random.randint(0, bh-ih)
    bg = bg.crop((left, upper, left+iw, upper+ih))
    bg.alpha_composite(image)
    return bg

def rotate(image):
    return image.rotate(random.randint(0, 359))

def brightness(image):
    return ImageEnhance.Brightness(image).enhance(round(random.uniform(0.8, 1.2), 2))

def saturation(image):
    return ImageEnhance.Color(image).enhance(round(random.uniform(0.7, 1.3), 2))

def shift(image, s):
    a = 1
    b = 0
    c = random.randint(s*-1, s)
    d = 0
    e = 1
    f = random.randint(s*-1, s)
    return image.transform(image.size, Image.AFFINE, (a, b, c, d, e, f))