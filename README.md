# LambdaBot

This is a discord bot whose main purpose is generating random Half-Life memes by combining one or more source images with a meme template (inspired by shitpostbot 5000). It can do a whole bunch of other things as well.

The bot is in constant development, so there may be bugs here and there, but for the most part it works *pretty well*™. Once added to the server, no further configuration is required.

[Add LambdaBot to your server](http://lambdabot.morchkovalski.com/invite)

### Things you don't necessarily have to know, but may be interested in:

#### Command prefix
By default, all of the bot's commands begin with `!`. You can change this using the !prefix command.

#### Disabling commands
If you don't want users using certain commands, you can disable them either in the whole server or on a per-channel basis using the !svcmd and !cmd commands respectively.

#### Image pools
This is something that will be expanded upon in future updates. Basically, for every channel a server manager is able to specify what kind of images should be used to generate memes. Currently there are 3 image pools available:
* `templates` - contains all the meme templates
* `halflife` - contains source images related to Half-Life
* `garfield` - contains source images related to Garfield (don't ask why)

By default the bot uses the `halflife` and `templates` pools. You can alter this using the !pool command.

The idea is to eventually allow server managers to create their own image pools to use within their servers. No ETA on when that happens though. I won't go into more detail for now.

#### Template submissions

Right now this is the very first thing on my to-do list. Basically a web interface where users can submit templates, because currently I have to do it all by hand myself which is a pain in the ass.

### Tech support

If you need any help besides what is described here and in the bot's !help command, or if you have any suggestions, you can find me in the [Half-Life discord](https://discord.gg/halflife) (`@yackson#8618`)
