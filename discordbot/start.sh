#!/bin/bash
stty rows 30
stty cols 100
source /srv/lambdabot.morchkovalski.com/venv/bin/activate
cd /srv/lambdabot.morchkovalski.com/lambdabot/discordbot
while true; do
    PYTHONPATH=/srv/lambdabot.morchkovalski.com/lambdabot python start.py
    sleep 5
done
