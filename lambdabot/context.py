import os
import random
import re
import sqlite3

from lambdabot.settings import *

SYS_RANDOM = random.SystemRandom()


def connect_context_db(context):
    """ connect to db, create if doesn't exist """

    db_file = DATA_DIR + '/contexts/' + context + '.db'
    os.makedirs(DATA_DIR + '/contexts', exist_ok=True)
    exists = os.path.isfile(db_file)
    if not exists:
        open(db_file, 'a').close()

    c = sqlite3.connect(db_file)
    c.execute('create table if not exists template_queue (template_name)')
    c.execute('create table if not exists sourceimg_queue (sourceimg_name)')
    c.commit()
    return c


def next_template(context):
    """ returns next template filename """

    c = connect_context_db(context)

    # read queue from db
    result = [row[0] for row in c.execute('select * from template_queue').fetchall()]

    # if empty, make new queue
    if len(result) == 0:

        # get list of templates
        available_templates = []
        for template_name, template_data in TEMPLATES.items():
            template_context = template_data.get('context')
            if template_context is None or template_context == context or\
                    (type(template_context) is list and context in template_context):
                available_templates.append(template_name)

        # create queue
        SYS_RANDOM.shuffle(available_templates)
        template_queue = available_templates[0:(min(TEMPLATE_QUEUE_LENGTH, len(available_templates)))]

        # get one template and remvoe it from queue
        template = template_queue.pop()

        # save queue to db
        for t in template_queue:
            c.execute('insert into template_queue(template_name) values (?)', (t,))

    # otherwise, get one template and remove it from queue
    else:
        template = result.pop()
        c.execute('delete from template_queue where template_name = ?', (template,))

    c.commit()
    c.close()

    if not os.path.isfile(TEMPLATE_DIR + '/' + template):
        raise FileNotFoundError
    else:
        return template


def next_sourceimg(context):
    """ returns next source image filename """

    c = connect_context_db(context)

    # read queue from db
    result = [row[0] for row in c.execute('select * from sourceimg_queue').fetchall()]

    # if empty, make new queue
    if len(result) == 0:

        # add common source images to list
        available_sourceimgs = \
            [file for file in os.listdir(SOURCEIMG_DIR) if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE)]

        # add context's source images to list
        if os.path.isdir(SOURCEIMG_DIR + '/' + context):
            available_sourceimgs += \
                (context + '/' + file for file in os.listdir(SOURCEIMG_DIR + '/' + context)
                 if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE))

        if len(available_sourceimgs) == 0:
            raise FileNotFoundError

        # create queue
        SYS_RANDOM.shuffle(available_sourceimgs)
        sourceimg_queue = available_sourceimgs[0:(min(SOURCEIMG_QUEUE_LENGTH, len(available_sourceimgs)))]

        # get one source image and remvoe it from queue
        sourceimg = sourceimg_queue.pop()

        # save queue to db
        for s in sourceimg_queue:
            c.execute('insert into sourceimg_queue(sourceimg_name) values (?)', (s,))

    # otherwise, get one source image and remove it from queue
    else:
        sourceimg = result.pop()
        c.execute('delete from sourceimg_queue where sourceimg_name = ?', (sourceimg,))

    c.commit()
    c.close()

    return sourceimg
