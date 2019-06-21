#!/usr/bin/env bash
set -e
venv/bin/python manage.py collectstatic --noinput
venv/bin/python manage.py compress
venv/bin/python manage.py migrate
sudo service apache2 reload
sudo systemctl restart lambdabot.service
