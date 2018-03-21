from discordbot.util import discord_send


class DiscordCommandException(Exception):
    pass


class DiscordSyntaxException(DiscordCommandException):
    pass


class DiscordCommandResponse:
    def __init__(self, message='', embed=None, attachment=None):
        self.message = message
        self.embed = embed
        self.attachment = attachment

    async def send(self, client, message):
        if self.attachment:
            await discord_send(
                client.send_file,
                message.channel,
                self.attachment,
                content="{} {}".format(message.author.mention, self.message)
            )
        else:
            await discord_send(
                client.send_message,
                message.channel,
                "{} {}".format(message.author.mention, self.message),
                embed=self.embed
            )
