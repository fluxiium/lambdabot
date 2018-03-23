class DiscordCommandException(Exception):
    pass


class DiscordSyntaxException(DiscordCommandException):
    pass


class DiscordCommandResponse:
    def __init__(self, message='', embed=None, attachment=None):
        self.__message = message
        self.__embed = embed
        self.__attachment = attachment

    async def send(self, client, message):
        if self.__attachment:
            await client.send_file(
                message.channel,
                self.__attachment,
                content="{} {}".format(message.author.mention, self.__message)
            )
        else:
            await client.send_message(
                message.channel,
                "{} {}".format(message.author.mention, self.__message),
                embed=self.__embed
            )
