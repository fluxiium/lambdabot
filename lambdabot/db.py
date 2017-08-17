import os
import sqlite3
import uuid
import datetime

from lambdabot.context import next_sourceimg, next_template
from lambdabot.settings import *


def connect_db():
    """ connect to db, create if doesn't exist """

    db_file = DATA_DIR + '/data.db'
    os.makedirs(DATA_DIR, exist_ok=True)
    exists = os.path.isfile(db_file)
    if not exists:
        open(db_file, 'a').close()

    c = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
    c.execute('create table if not exists memes (meme_id, num, template_name, context, gen_date timestamp)')
    c.execute('create table if not exists memes_sourceimgs (meme_id, slot_id, sourceimg_name)')
    c.execute('create table if not exists urls (url, physical_path, content_type)')
    c.commit()
    return c


# todo: blacklist for template

def make_meme(context, template_file=None):
    """ generates a random meme """

    template_file = template_file or next_template(context)

    source_files = []
    for _ in TEMPLATES[template_file]['src']:
        # pick source file that hasn't been used
        while True:
            source_file = next_sourceimg(context)
            if source_file not in source_files:
                break
        source_files.append(source_file)

    gen_date = datetime.datetime.now()

    c = connect_db()
    meme_id = str(uuid.uuid4())
    meme_count = c.execute('select count(meme_id) from memes').fetchone()[0] + 1

    c.execute('insert into memes(meme_id, num, template_name, context, gen_date) values (?, ?, ?, ?, ?)',
              (meme_id, meme_count, template_file, context, gen_date))
    for source_file, slot_id in zip(source_files, range(0, len(TEMPLATES[template_file]['src']))):
        c.execute('insert into memes_sourceimgs(meme_id, slot_id, sourceimg_name) values (?, ?, ?)',
                  (meme_id, slot_id, source_file))
    c.commit()
    c.close()

    return meme_id


def meme_info(meme_id):
    """ load info about meme """

    c = connect_db()
    result = c.execute('select template_name, context, gen_date, num from memes where meme_id = ?', (meme_id,))\
        .fetchall()

    if len(result) == 0:
        raise KeyError

    template_name = result[0][0]
    context = result[0][1]
    gen_date = result[0][2]
    num = result[0][3]

    result = c.execute('select slot_id, sourceimg_name from memes_sourceimgs where meme_id = ? order by slot_id asc',
                       (meme_id,)).fetchall()

    source_images = [row[1] for row in result]

    return template_name, source_images, context, gen_date, num


def get_resource_path(url):
    """ get physical path to resource based on url """

    c = connect_db()
    result = c.execute('select physical_path, content_type from urls where url = ?', (url,)).fetchall()

    if len(result) == 0:
        return None, None

    return result[0][0], result[0][1]


def get_resource_url(physical_path, content_type):
    """ get resource url based on physical path (generate if doesn't exist) """

    c = connect_db()
    result = c.execute('select url from urls where physical_path = ? and content_type = ?',
                       (physical_path, content_type)).fetchall()

    if len(result) == 0:
        url = str(uuid.uuid4())
        c.execute('insert into urls(url, physical_path, content_type) values (?, ?, ?)',
                  (url, physical_path, content_type))
        c.commit()
    else:
        url = result[0][0]

    return url


def meme_info_page(meme_id):
    template_file, source_files, context, gen_date, num = meme_info(meme_id)
    template_bg_file = TEMPLATES[template_file].get('bgimg')

    template_url = get_resource_url(os.path.join(TEMPLATE_DIR_LOCAL, template_file), 'image/png')
    template_bg_url = get_resource_url(os.path.join(TEMPLATE_DIR_LOCAL, template_bg_file), 'image/png')\
        if template_bg_file is not None else None
    source_urls = [get_resource_url(os.path.join(SOURCEIMG_DIR_LOCAL, source_file), 'image/png')
                   for source_file in source_files]
    return template_url, template_bg_url, source_urls, context, gen_date, num
