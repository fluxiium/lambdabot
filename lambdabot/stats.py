import os
import re
import math

from settings import *


def binom(x, y):
    if y == x:
        return 1
    elif y == 1:
        return x
    elif y > x:
        return 0
    else:
        a = math.factorial(x)
        b = math.factorial(y)
        c = math.factorial(x-y)
        div = a // (b * c)
        return div

possible_memes = 0
sourceimgs = len([file for file in os.listdir(SOURCEIMG_DIR) if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE)])

for _, template in TEMPLATES.items():
    possible_memes += binom(sourceimgs, len(template.get('src')))

print(possible_memes)
