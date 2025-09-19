#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Debug environment variables
python debug_env.py

python manage.py collectstatic --noinput
python manage.py migrate
