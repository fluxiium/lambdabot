import facebook

# http://nodotcom.org/python-facebook-tutorial.html
import sys
from lambdabot.settings import *

cfg = {
    "page_id": "486920085001034",  # lambdabot
    "access_token": sys.argv[1],
}

graph = facebook.GraphAPI(cfg['access_token'])
resp = graph.get_object('me/accounts')
page_access_token = None
for page in resp['data']:
    if page['id'] == cfg['page_id']:
        page_access_token = page['access_token']

token_file = open(os.path.join(DATA_DIR, 'fbtoken.txt'), 'w')
token_file.write(page_access_token)
token_file.close()
