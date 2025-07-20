#!/usr/bin/env bash
# exit on error
set -o errexit

# This script tells Render how to build your app.

# 1. Install pipenv
pip install pipenv

# 2. Use pipenv to install all dependencies from Pipfile.lock
pipenv install --deploy --system

# 3. Run your standard Django production commands
python manage.py collectstatic --no-input
python manage.py migrate