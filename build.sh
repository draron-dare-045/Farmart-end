#!/usr/bin/env bash
# exit on error
set -o errexit

# NEW SECTION: Install system-level dependencies
# -----------------------------------------------
# This is for packages like lxml that need to be compiled
# and require system C libraries and build tools.
apt-get update
apt-get install -y build-essential libxml2-dev libxslt1-dev

# --- Your original build commands ---
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate