#!/bin/bash
source /srv/lambdabot.morchkovalski.com/venv/bin/activate
cd /srv/lambdabot.morchkovalski.com/lambdabot/discordbot
while true; do
    PYTHONPATH=/srv/lambdabot.morchkovalski.com/lambdabot python hldiscord.py
    sleep 5
done
