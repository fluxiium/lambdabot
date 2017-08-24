import os

from PIL import Image
from PIL import ImageFilter

from lamdabotweb.settings import MEME_TEMPLATES, TEMPLATE_DIR, SOURCEIMG_DIR, RESOURCE_DIR


def preview_meme(meme, add_watermark=False):
    """ retrieve a previously generated meme """

    meme_file = meme.get_local_path()

    if os.path.isfile(meme_file):
        return Image.open(meme_file)
    else:
        template_file = meme.template
        source_files = meme.get_sourceimgs()

    template_data = MEME_TEMPLATES[template_file]
    template_bg_file = template_data.get('bgimg')

    foreground = Image.open(os.path.join(TEMPLATE_DIR, template_file)).convert("RGBA")
    if template_bg_file is None:
        background = Image.new(foreground.mode, foreground.size, template_data.get('bg', 'black'))
    else:
        background = Image.open(os.path.join(TEMPLATE_DIR, template_bg_file)).convert('RGBA')

    for source_file, slot_id in zip(source_files, range(0, len(MEME_TEMPLATES[template_file]['src']))):

        source_image_original = Image.open(os.path.join(SOURCEIMG_DIR, source_file)).convert("RGBA")
        sources_data = MEME_TEMPLATES[template_file]['src'][slot_id]

        if not type(sources_data) is list:
            sources_data = [sources_data]

        for source_data in sources_data:
            # resize, crop, and rotate source image
            source_image = source_image_original.copy()

            if source_data.get('cover'):
                resize_ratio = max(source_data['w'] / source_image.size[0], source_data['h'] / source_image.size[1])
            else:
                resize_ratio = min(source_data['w'] / source_image.size[0], source_data['h'] / source_image.size[1])

            source_image = source_image.resize(
                [int(source_image.size[0] * resize_ratio), int(source_image.size[1] * resize_ratio)], Image.ANTIALIAS)

            if source_data.get('cover'):
                source_image = source_image.crop((
                    (source_image.size[0] - source_data['w']) / 2,
                    (source_image.size[1] - source_data['h']) / 2,
                    (source_image.size[0] + source_data['w']) / 2,
                    (source_image.size[1] + source_data['h']) / 2,
                ))

            rotate_angle = source_data.get('rotate')
            if rotate_angle:
                source_image = source_image.rotate(rotate_angle, resample=Image.BICUBIC, expand=True)

            # get info for pasting
            source_alpha = source_image.copy()
            paste_pos = (
                int(source_data['x'] + (source_data['w'] - source_image.size[0]) / 2),
                int(source_data['y'] + (source_data['h'] - source_image.size[1]) / 2),
            )

            # apply effects
            if source_data.get('blur'):
                source_image = source_image.filter(ImageFilter.GaussianBlur(3))

            if source_data.get('grayscale'):
                source_image = source_image.convert('LA')

            if source_data.get('mask'):
                # paste on background layer
                background.paste(source_image, paste_pos, source_alpha)
            else:
                # paste on foreground layer
                foreground.paste(source_image, paste_pos, source_alpha)

    meme_image = Image.alpha_composite(background, foreground)

    if add_watermark:
        # load watermark
        watermark_image = Image.open(RESOURCE_DIR + '/watermark.png').convert("RGBA")

        # create final canvas
        watermarked_meme_image = Image.new(
            meme_image.mode,
            (meme_image.size[0], meme_image.size[1] + watermark_image.size[1])
        )

        # paste meme and watermark
        watermarked_meme_image.paste(meme_image, (0, 0), meme_image)
        watermarked_meme_image.paste(watermark_image,
                                     (0, meme_image.size[1]), watermark_image)

        meme_image = watermarked_meme_image

    meme_image = meme_image.convert('RGB')
    meme_image.save(meme_file)
    return meme_image
