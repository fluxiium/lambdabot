import json
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from discordbot.models import DiscordServerUser, DiscordUser, DiscordSourceImgSubmission, MurphyRequest, \
    DiscordMeem

f = open('../tests/lambdabot2.json', 'r')
data = json.load(f)
f.close()

models = {
    'discordbot.discordsourceimgsubmission': DiscordSourceImgSubmission,
    'discordbot.discordmeem': DiscordMeem,
    'discordbot.murphyrequest': MurphyRequest,
}
users = {}
num = 0

for obj in data:
    if obj['model'] != 'discordbot.discordserveruser':
        continue
    users[obj['pk']] = obj['fields']

for obj in data:
    num += 1
    print(num)

    if obj['model'] not in models.keys():
        continue

    if obj['fields']['server_user'] is None:
        continue

    u = users[obj['fields']['server_user']]

    subm = models[obj['model']].objects.filter(pk=obj['pk']).first()
    if subm is None:
        continue

    existing = DiscordServerUser.objects.filter(user__user_id=u['user'], server__server_id=u['server']).first() or \
        DiscordServerUser.objects.create(user_id=u['user'], server_id=u['server'])
    subm.server_user = existing
    subm.save()

for usr in DiscordServerUser.objects.all():
    if usr.discordsourceimgsubmission_set.count() + usr.discordmeem_set.count() + usr.murphyrequest_set.count() == 0:
        usr.delete()

for usr in DiscordUser.objects.all():
    if usr.discordserveruser_set.count() == 0:
        usr.delete()
