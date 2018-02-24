import facebook

# http://nodotcom.org/python-facebook-tutorial.html
import sys

graph = facebook.GraphAPI(sys.argv[2])
resp = graph.get_object('me/accounts')
page_access_token = None
for page in resp['data']:
    if page['id'] == sys.argv[1]:
        print(page['access_token'])
