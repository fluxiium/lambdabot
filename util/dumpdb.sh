#!/bin/bash
source /srv/lambdabot.morchkovalski.com/venv/bin/activate
PYTHONPATH=/srv/lambdabot.morchkovalski.com/lambdabot /srv/lambdabot.morchkovalski.com/lambdabot/manage.py dumpdata > /home/morchv/lambdabot.json
