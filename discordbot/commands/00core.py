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

    limit_count, limit_time, limit_left = member.get_limit(DiscordServerUser.ACTION_MEEM)
    if limit_left > 0:
        return DiscordCommandResponse(get_timeout_str(
                "you can only generate {0} memes every {1} minutes. Please wait {2}.",
                limit_count, limit_time, limit_left
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
    if len(attachments) < 1:
        raise DiscordSyntaxException

    attachment = attachments[0]
    submitted_file = save_attachment(attachment['real_url'], attachment.get('filename'))

    limit_count, limit_time, limit_left = member.get_limit(DiscordServerUser.ACTION_SUBMIT_SRCIMG)
    if limit_left > 0:
        return DiscordCommandResponse(get_timeout_str(
                "you can only submit {0} images every {1} minutes. Please wait {2}.",
                limit_count, limit_time, limit_left
            ))

    submission = MemeSourceImage.submit(submitted_file, attachment.get('filename', None))
    if submission is None:
        return DiscordCommandResponse(
            "the image is too big or invalid format! (supported jpeg/png < {0} KB)".format(MAX_SRCIMG_SIZE / 1000)
        )

    DiscordSourceImgSubmission.objects.create(server_user=member, sourceimg=submission)

    log('sourceimg submitted by {}'.format(member))
    return DiscordCommandResponse("thanks! The source image will be added once it's approved.")

COMMANDS['submit'] = {
    'function': _cmd_submit,
    'help': 'submit a source image for the meme generator',
    'usage': '(attachment | embed)'
}
