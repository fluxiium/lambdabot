import json
import random
import textwrap
import datetime
import re
import requests

from bs4 import BeautifulSoup
from discord import Embed
from django.utils import timezone

import os

from discordbot.models import DiscordSourceImgSubmission, DiscordMeem
from discordbot.util import delay_send, save_attachment, log, log_exc, headers
from memeviewer.models import MemeSourceImage, MemeTemplate, Meem, Setting
from memeviewer.preview import preview_meme


async def cmd_help(client, server, member, message, **_):
    helpstr = "{0} available commands:".format(message.author.mention)
    for cmd_data in member.get_commands():
        if cmd_data.hidden:
            continue

        helpstr += "\n`{0}{1}".format(server.prefix, cmd_data.cmd)

        if cmd_data.help_params:
            helpstr += " {}`".format(cmd_data.help_params)
        else:
            helpstr += "`"

        if cmd_data.help:
            helpstr += " - {0}".format(cmd_data.help)

    await delay_send(client.send_message, message.channel, helpstr)


async def cmd_meem(client, server, member, message, args, argstr, attachment, **_):

    await delay_send(client.send_typing, message.channel)

    template = None

    if len(args) > 1:
        if args[1].lower() == "submit" and attachment is not None:
            submitted_file = save_attachment(attachment)
            submit_limit_count, submit_limit_time = member.get_submit_limit()
            last_user_submits = member.get_submits(limit=submit_limit_count)
            if last_user_submits.count() >= submit_limit_count:
                submit_delta = datetime.timedelta(minutes=submit_limit_time)
                submit_time = last_user_submits[submit_limit_count - 1].sourceimg.add_date
                if timezone.now() - submit_delta <= submit_time:
                    seconds_left = int(((submit_time + submit_delta) - timezone.now()).total_seconds()) + 1
                    if seconds_left >= 3 * 60:
                        timestr = "{0} more minutes".format(int(seconds_left / 60) + 1)
                    else:
                        timestr = "{0} more seconds".format(seconds_left)
                    await delay_send(
                        client.send_message,
                        message.channel,
                        "{3} you can only submit {0} images every {1} minutes. Please wait {2}.".format(
                            submit_limit_count,
                            submit_limit_time,
                            timestr,
                            message.author.mention,
                        )
                    )
                    return

            submission_stat = os.stat(submitted_file)
            max_srcimg_size = int(Setting.get('max srcimg size', '1500000'))
            if submission_stat.st_size > max_srcimg_size:
                await delay_send(
                    client.send_message,
                    message.channel,
                    "{0} the image is too big! (max {1} KB)".format(message.author.mention, max_srcimg_size / 1000)
                )
                return

            submission = MemeSourceImage.submit(submitted_file, attachment.get('filename', None))
            discord_submission = DiscordSourceImgSubmission(server_user=member, sourceimg=submission)
            discord_submission.save()

            await delay_send(
                client.send_message,
                message.channel,
                "{0} thanks! The source image will be added once it's approved.".format(message.author.mention)
            )

            log('sourceimg submitted by {}'.format(member))

            return

        else:
            template_name = argstr
            if template_name == '^':
                template = MemeTemplate.find(server.context)
            else:
                template = MemeTemplate.find(template_name)
                if template is None:
                    await delay_send(
                        client.send_message,
                        message.channel,
                        "{0} template `{1}` not found :cry:".format(message.author.mention, template_name)
                    )
                    return

    meme_limit_count, meme_limit_time = member.get_meme_limit()
    last_user_memes = member.get_memes(limit=meme_limit_count)
    if last_user_memes.count() >= meme_limit_count:
        meme_delta = datetime.timedelta(minutes=meme_limit_time)
        meme_time = last_user_memes[meme_limit_count - 1].meme.gen_date
        if timezone.now() - meme_delta <= meme_time:
            seconds_left = int(((meme_time + meme_delta) - timezone.now()).total_seconds()) + 1
            if seconds_left >= 3 * 60:
                timestr = "{0} more minutes".format(int(seconds_left / 60) + 1)
            else:
                timestr = "{0} more seconds".format(seconds_left)
            await delay_send(
                client.send_message,
                message.channel,
                "{3} you can only generate {0} memes every {1} minutes. Please wait {2}.".format(
                    meme_limit_count,
                    meme_limit_time,
                    timestr,
                    message.author.mention,
                )
            )
            return

    meme = Meem.generate(context=server.context, template=template)
    preview_meme(meme)

    discord_meme = DiscordMeem(meme=meme, server_user=member, channel_id=message.channel.id)
    discord_meme.save()

    await delay_send(
        client.send_message,
        message.channel,
        "{0} here's a meme (using template `{2}`)\n{1}".format(message.author.mention, meme.get_info_url(), meme.template_link)
    )

    discord_meme.mark_sent()

    log('meme generated:', meme)


async def cmd_led(client, server, member, message, args, argstr, **_):
    await delay_send(client.send_typing, message.channel)

    if len(args) == 1:
        await delay_send(
            client.send_message,
            message.channel,
            "{0} usage: `{1} (text)`".format(message.author.mention, args[0]),
        )
        return

    response = requests.post('http://wigflip.com/signbot/', data={
        'T': argstr,
        'S': 'L',
    }, headers=headers)

    soup = BeautifulSoup(response.content.decode('utf-8'), "html5lib")
    img = soup.select_one('#output img')
    if img is not None:
        await delay_send(
            client.send_message,
            message.channel,
            "{0} {1}".format(message.author.mention, img['src']),
        )
    else:
        await delay_send(
            client.send_message,
            message.channel,
            "{0} error :cry:".format(message.author.mention),
        )


async def cmd_mario(client, server, member, message, args, argstr, **_):
    await delay_send(client.send_typing, message.channel)

    if len(args) < 3 or len(args) > 4:
        await delay_send(
            client.send_message,
            message.channel,
            '{0} usage: `{1} ["name"] "first line" "message"`'.format(message.author.mention, args[0]),
        )
        return

    if len(args) == 4:
        name = args[1]
        title = args[2]
        msgtext = args[3]
    else:
        name = None
        title = args[1]
        msgtext = args[2]

    response = requests.post('http://wigflip.com/thankyoumario/', data={
        'name': name,
        'title': title,
        'lines': msgtext,
        'double': 'y',
    }, headers=headers)

    soup = BeautifulSoup(response.content.decode('utf-8'), "html5lib")
    img = soup.select_one('#output img')
    if img is not None:
        await delay_send(
            client.send_message,
            message.channel,
            "{0} {1}".format(message.author.mention, img['src']),
        )
    else:
        await delay_send(
            client.send_message,
            message.channel,
            "{0} error :cry:".format(message.author.mention),
        )


async def cmd_noviews(client, server, member, message, args, **_):
    await delay_send(client.send_typing, message.channel)

    attempt = 0
    videourl = None
    while videourl is None and attempt < 5:
        try:
            response = requests.get('http://www.petittube.com', headers=headers)
            soup = BeautifulSoup(response.content.decode('utf-8'), "html5lib")
            videourl = re.search('\/(\w+)\?', soup.select_one('iframe')['src']).groups()[0]
        except Exception as e:
            attempt += 1

    if videourl is None:
        await delay_send(
            client.send_message,
            message.channel,
            "{0} error :cry:".format(message.author.mention),
        )
    else:
        await delay_send(
            client.send_message,
            message.channel,
            "{0} https://youtu.be/{1}".format(message.author.mention, videourl),
        )


async def cmd_wiki(client, server, member, message, args, argstr, **_):
    await delay_send(client.send_typing, message.channel)

    wiki_url = Setting.get('hl wiki url', 'http://combineoverwiki.net')
    article = None
    was_random = False

    if len(args) == 1:
        # noinspection PyShadowingNames
        try:
            was_random = True
            response = requests.get(
                '{0}/api.php?action=query&generator=random&grnnamespace=0&grnlimit=1&prop=info&inprop=url&format=json'.format(wiki_url),
                headers=headers,
            )
            article_data = json.loads(response.content.decode('utf-8'))
            article = next(iter(article_data['query']['pages'].values()))

        except Exception as exc:
            log_exc(exc)

    else:
        # noinspection PyShadowingNames
        try:
            query = argstr
            response = requests.get(
                '{0}/api.php?action=query&generator=search&gsrsearch={1}&gsrlimit=1&prop=info&inprop=url&format=json'.format(wiki_url, query),
                headers=headers,
            )
            article_data = json.loads(response.content.decode('utf-8'))
            if article_data.get('query') is not None:
                article = next(iter(article_data['query']['pages'].values()))
        except Exception as exc:
            log_exc(exc)

    proceed = False
    soup = None

    while not proceed:
        if article is None:
            await delay_send(
                client.send_message,
                message.channel,
                "{0} article not found :cry:".format(message.author.mention)
            )
            return

        response = requests.get(article['fullurl'], headers=headers)
        soup = BeautifulSoup(response.content.decode('utf-8'), "html5lib")

        heading = soup.select_one('#firstHeading')
        if not was_random or heading is None or not heading.getText().lower().endswith('(disambiguation)'):
            proceed = True
        else:
            page_links = soup.select('#mw-content-text > ul:nth-of-type(1) > li')
            random_page = random.choice([li.select_one('a:nth-of-type(1)').getText() for li in page_links])
            if random_page is None:
                article = None
            else:
                response = requests.get(
                    '{0}/api.php?action=query&generator=search&gsrsearch={1}&gsrlimit=1&prop=info&inprop=url&format=json'.format(
                        wiki_url, random_page),
                    headers=headers,
                )
                article_data = json.loads(response.content.decode('utf-8'))
                if article_data.get('query') is not None:
                    article = next(iter(article_data['query']['pages'].values()))

    pic_tag = soup.select_one('td.infoboximage > a > img')
    if pic_tag is None:
        pic_tag = soup.select_one('img.thumbimage')

    desc_tag = soup.select_one('div#mw-content-text > p:nth-of-type(2)')
    desc = textwrap.shorten(desc_tag.getText(), width=250) if desc_tag is not None else None

    embed = Embed(
        title=article['title'],
        url=article['fullurl'],
        color=0xF7923A,
        description=desc,
    )
    embed.set_footer(
        text="Combine Overwiki",
        icon_url="http://combineoverwiki.net/images/1/12/HLPverse.png".format(wiki_url)
    )

    if pic_tag is not None:
        embed.set_thumbnail(url="{0}{1}".format(wiki_url, pic_tag['src']))
        # embed.set_image(url="{0}{1}".format(wiki_url, pic_tag['src']))

    await delay_send(
        client.send_message,
        message.channel,
        "{0} {1}".format(message.author.mention, article['fullurl']),
        embed=embed,
    )


async def cmd_test(client, message, **_):
    await delay_send(client.send_message, client.get_channel("291537367452614658"), "test")
