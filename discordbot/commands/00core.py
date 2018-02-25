import datetime
from django.utils import timezone
from discordbot.models import DiscordSourceImgSubmission, DiscordMeem
from discordbot.util import discord_send, save_attachment, log
from lamdabotweb.settings import MAX_SRCIMG_SIZE
from memeviewer.models import MemeSourceImage, MemeTemplate, Meem
from memeviewer.preview import preview_meme

COMMANDS = {}


async def _cmd_meem(client, server, member, message, args, argstr, attachment, dl_embed_url, **_):

    await discord_send(client.send_typing, message.channel)

    template = None

    if len(args) > 1:
        if args[1].lower() == "submit" and attachment is not None:
            if dl_embed_url is None:
                submitted_file = save_attachment(attachment['proxy_url'], attachment['filename'])
            else:
                submitted_file = save_attachment(dl_embed_url)
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
                    await discord_send(
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

            submission = MemeSourceImage.submit(submitted_file, attachment.get('filename', None))
            if submission is None:
                await discord_send(
                    client.send_message,
                    message.channel,
                    "{0} the image is too big or invalid format! (supported jpeg/png < {1} KB)".format(
                        message.author.mention, MAX_SRCIMG_SIZE / 1000)
                )
                return

            discord_submission = DiscordSourceImgSubmission(server_user=member, sourceimg=submission)
            discord_submission.save()

            await discord_send(
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
                    await discord_send(
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
            await discord_send(
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

    await discord_send(
        client.send_message,
        message.channel,
        "{0} here's a meme (using template `{2}`)\n{1}".format(message.author.mention, meme.get_info_url(), meme.template_link)
    )

    log(message.author, 'meme generated:', meme)

COMMANDS['meem'] = {
    'function': _cmd_meem,
    'help': 'generate a random meme',
    'usage': '[ [template name] | ^ | submit (url) ]'
}

COMMAND_ALIASES = {
    'meemay': 'meem',
    'mem': 'meem',
    'meme': 'meem',
    'memuch': 'meem',
    'miejm': 'meem',
}
