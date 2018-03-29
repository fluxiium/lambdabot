import os
import discord
import requests
import traceback
import uuid
from tempfile import mkdtemp
from django.utils import timezone

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'
}


def log(*args, tag=None):
    if tag is not None:
        tag = "[{}]".format(tag)
    else:
        tag = ""
    print(timezone.now(), tag, *args)


def log_exc(exc):
    log("--- ERROR ---")
    print(exc)
    print(traceback.format_exc())


def get_timeout_str(message, limit, timeout, left):
    if left >= 3 * 60:
        timestr = "{0} more minutes".format(int(left / 60) + 1)
    else:
        timestr = "{0} more seconds".format(left)
    return message.format(limit, timeout, timestr)


class DiscordImage:
    def __init__(self, att, is_embed):
        self.__att = att
        self.__is_embed = is_embed

    @classmethod
    def get_from_message(cls, msg: discord.Message):
        images = []
        for att in msg.attachments:
            images.append(cls.__from_attachment(att))
        for emb in msg.embeds:
            try:
                images.append(cls.__from_embed(emb))
            except AttributeError:
                pass
        return images

    @classmethod
    def __from_embed(cls, embed: discord.Embed):
        if embed.image != discord.Embed.Empty:
            return cls(embed.image.url, True)
        elif embed.thumbnail != discord.Embed.Empty:
            return cls(embed.thumbnail.url, True)
        else:
            raise AttributeError

    @classmethod
    def __from_attachment(cls, attachment: discord.Attachment):
        return cls(attachment, False)

    def save(self):
        tmpdir = mkdtemp(prefix="lambdabot_attach_")
        if self.__is_embed:
            filename = os.path.join(tmpdir, str(uuid.uuid4()))
        else:
            filename = os.path.join(tmpdir, self.__att.filename)
        url = self.get_url()
        log('saving image: {0} -> {1}'.format(url, filename))
        attachment = requests.get(url, headers=headers)
        with open(filename, 'wb') as attachment_file:
            attachment_file.write(attachment.content)
        return filename

    def get_url(self):
        if self.__is_embed:
            return self.__att
        else:
            return self.__att.proxy_url

    def is_embed(self):
        return self.__is_embed
