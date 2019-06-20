import subprocess
from PIL import Image
from tempfile import mkdtemp
from discordbot import settings

PNG_DIR = settings.BASE_DIR + '/discordbot/cogs/extra/danceimg/'
SPACE_IMAGE = Image.new('RGBA', (100, 100), (0, 0, 0, 0))


def _make_frame(i, text):
    images = {}
    height = 0
    width = 0
    for c in text:
        if c in 'qwertyuiopasdfghjklzxcvbnm1234567890@$&!_':
            cim = Image.open('%s%s/%02d.png' % (PNG_DIR, c, i)).convert('RGBA')
        else:
            cim = SPACE_IMAGE
        images[c] = cim
        width += cim.size[0]
        height = max(height, cim.size[1])
    bg = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    x = 0
    for c in text:
        cim = images[c]
        bg.paste(cim, (x, height - cim.size[1]), cim)
        x += cim.size[0]
    return bg


def dance(text):
    tmpdir = mkdtemp(prefix="lambdabot_dance_")
    text = text[:settings.DANCE_MAX_LEN].replace('?', '_').lower()
    for i in range(14):
        frame = _make_frame(i, text)
        if frame.size[0] > settings.DANCE_MAX_W:
            scale_factor = settings.DANCE_MAX_W / frame.size[0]
            frame = frame.resize([int(scale_factor * d) for d in frame.size], Image.ANTIALIAS)
        frame.save('%s/%d.png' % (tmpdir, i))
    # convert -dispose previous -delay 20 -loop 0 *.png img.gif
    process = subprocess.Popen('"{0}" -dispose 2 -delay 20 -loop 0 "{1}/*.png" "{1}/dance.gif"'.format(settings.IMAGEMAGICK_PATH, tmpdir), shell=True)
    process.wait()
    return tmpdir
