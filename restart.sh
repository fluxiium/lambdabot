#!/usr/bin/env bash
set -e
sudo service apache2 reload
sudo systemctl restart lambdabot.service
