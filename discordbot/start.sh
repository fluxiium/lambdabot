#!/bin/bash
stty rows 30
stty cols 100
source /srv/lambdabot.morchkovalski.com/venv/bin/activate
PYTHONPATH=/srv/lambdabot.morchkovalski.com/lambdabot python /srv/lambdabot.morchkovalski.com/lambdabot/discordbot/start.py
