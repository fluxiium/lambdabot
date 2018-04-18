import os
import json
import re
import requests
import config
from django.core.management import BaseCommand
from lamdabotweb.settings import BASE_DIR
from util import headers

_API_URL = 'https://graph.facebook.com/v2.10/'


class Command(BaseCommand):
    help = 'Gets a permanent access token for your facebook page'
    _config_regex = re.compile("FACEBOOK_PAGE_TOKEN = '[A-Za-z0-9]*'")

    def add_arguments(self, parser):
        parser.add_argument('temp_token')

    def handle(self, *args, **options):
        temp_token = options['temp_token']
        response = requests.get('{0}oauth/access_token?grant_type=fb_exchange_token&client_id={1}&client_secret={2}&fb_exchange_token={3}'.format(
            _API_URL, config.FACEBOOK_APP_ID, config.FACEBOOK_APP_SECRET, temp_token
        ), headers=headers)
        long_token = json.loads(response.content.decode('utf-8'))['access_token']
        response = requests.get('{0}me/accounts?access_token={1}'.format(_API_URL, long_token), headers=headers)
        for page in json.loads(response.content.decode('utf-8'))['data']:
            if page['id'] == config.FACEBOOK_PAGE_ID:
                perm_token = page['access_token']
                print('New access token:', perm_token)
                print('Updating config.py...')
                cfg_file = BASE_DIR + '/config.py'
                try:
                    os.remove(cfg_file + '~')
                except OSError:
                    pass
                os.rename(cfg_file, cfg_file + '~')
                with open(cfg_file + '~') as old_cfg, open(cfg_file, 'w') as new_cfg:
                    for line in old_cfg:
                        if self._config_regex.match(line):
                            new_cfg.write("FACEBOOK_PAGE_TOKEN = '%s'\n" % perm_token)
                        else:
                            new_cfg.write(line)
