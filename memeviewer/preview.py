import os

from PIL import Image
from PIL import ImageFilter

from lamdabotweb.settings import TEMPLATE_DIR, SOURCEIMG_DIR


def preview_meme(meme):
    """ return image based on meme data """

    meme_file = meme.get_local_path()

    if os.path.isfile(meme_file):
        return Image.open(meme_file)
    else:
        template = meme.template_link

    foreground = Image.open(os.path.join(TEMPLATE_DIR, template.name)).convert("RGBA")
    if template.bg_img == '':
        background = Image.new(foreground.mode, foreground.size, template.bg_color or 'black')
    else:
        background = Image.open(os.path.join(TEMPLATE_DIR, template.bg_img)).convert('RGBA')

    for srcimg_data in meme.get_sourceimgs():

        source_image_original = Image.open(os.path.join(SOURCEIMG_DIR, srcimg_data.source_image.name)).convert("RGBA")
        slot = srcimg_data.slot

        # resize, crop, and rotate source image
        source_image = source_image_original.copy()

        if slot.cover:
            resize_ratio = max(slot.w / source_image.size[0], slot.h / source_image.size[1])
        else:
            resize_ratio = min(slot.w / source_image.size[0], slot.h / source_image.size[1])

        source_image = source_image.resize(
            [int(source_image.size[0] * resize_ratio), int(source_image.size[1] * resize_ratio)], Image.ANTIALIAS)

        if slot.cover:
            source_image = source_image.crop((
                (source_image.size[0] - slot.w) / 2,
                (source_image.size[1] - slot.h) / 2,
                (source_image.size[0] + slot.w) / 2,
                (source_image.size[1] + slot.h) / 2,
            ))

        if slot.rotate != 0:
            source_image = source_image.rotate(slot.rotate, resample=Image.BICUBIC, expand=True)

        # get info for pasting
        source_alpha = source_image.copy()
        paste_pos = (
            int(slot.x + (slot.w - source_image.size[0]) / 2),
            int(slot.y + (slot.h - source_image.size[1]) / 2),
        )

        # apply effects
        if slot.blur:
            source_image = source_image.filter(ImageFilter.GaussianBlur(3))

        if slot.grayscale:
            source_image = source_image.convert('LA')

        if slot.mask:
            # paste on background layer
            background.paste(source_image, paste_pos, source_alpha)
        else:
            # paste on foreground layer
            foreground.paste(source_image, paste_pos, source_alpha)

    meme_image = Image.alpha_composite(background, foreground)

    meme_image = meme_image.convert('RGB')
    meme_image.save(meme_file)
    return meme_image
