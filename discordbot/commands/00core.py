from discordbot.classes import DiscordSyntaxException, DiscordCommandResponse
from discordbot.models import DiscordSourceImgSubmission, DiscordMeem, DiscordServerUser
from discordbot.util import save_attachment, log, get_timeout_str
from lamdabotweb.settings import MAX_SRCIMG_SIZE, DISCORD_SEND_ATTACHMENTS
from memeviewer.models import MemeSourceImage, MemeTemplate, Meem
from memeviewer.preview import preview_meme

COMMANDS = {}
COMMAND_ALIASES = {
    'meemay': 'meem',
    'mem': 'meem',
    'meme': 'meem',
    'memuch': 'meem',
    'miejm': 'meem',
}


async def _cmd_meem(server, member, message, args, argstr, **_):
    template = None

    if len(args) > 1:
        template_name = argstr
        if template_name == '^':
            template = MemeTemplate.find(server.context)
        else:
            template = MemeTemplate.find(template_name)
            if template is None:
                return DiscordCommandResponse("template `{}` not found :cry:".format(template_name))

    seconds_left, limit_count, limit_time = member.get_meme_limit()
    if seconds_left > 0:
        return DiscordCommandResponse(get_timeout_str(
                "you can only generate {0} memes every {1} minutes. Please wait {2}.",
                limit_count, limit_time, seconds_left
            ))

    meme = Meem.generate(context=server.context, template=template)
    preview_meme(meme)

    DiscordMeem.objects.create(meme=meme, server_user=member, channel_id=message.channel.id)
    log(message.author, 'meme generated:', meme)

    msgstr = "here's a meme (using template `{0}`)\n{1}".format(
        meme.template_link,
        DISCORD_SEND_ATTACHMENTS and ('<' + meme.get_info_url() + '>') or meme.get_info_url(),
    )

    return DiscordCommandResponse(msgstr, attachment=DISCORD_SEND_ATTACHMENTS and meme.get_local_path() or None)

COMMANDS['meem'] = {
    'function': _cmd_meem,
    'help': 'generate a random meme',
    'usage': '[template name | ^ ]'
}


async def _cmd_submit(member, attachments, **_):
    imgcount = len(attachments)

    if imgcount < 1:
        raise DiscordSyntaxException

    added = 0

    for attachment in attachments:
        submitted_file = save_attachment(attachment['real_url'], attachment.get('filename'))
        submission = MemeSourceImage.submit(submitted_file, attachment.get('filename', None))
        if submission is not None:
            added += 1
            sourceimg = DiscordSourceImgSubmission.objects.create(server_user=member, sourceimg=submission)
            log('sourceimg submitted by {}: {}'.format(member, sourceimg))

    if added == imgcount:
        if imgcount == 1:
            return DiscordCommandResponse("thanks! The source image will be added once it's approved.")
        else:
            return DiscordCommandResponse("thanks! The source images will be added once they're approved.")
    else:
        if imgcount == 1:
            return DiscordCommandResponse("the image is too big or invalid format! (supported jpeg/png < {} KB)".format(MAX_SRCIMG_SIZE / 1000))
        else:
            return DiscordCommandResponse("{}/{} images submitted. The rest is too big or invalid format! (supported jpeg/png < {} KB)".format(added, imgcount, MAX_SRCIMG_SIZE / 1000))

COMMANDS['submit'] = {
    'function': _cmd_submit,
    'help': 'submit a source image for the meme generator',
    'usage': '(attachment | embed)'
}
