#!/usr/bin/env bash
set -e
venv/bin/pip install -r requirements.txt --upgrade
./restart.sh
