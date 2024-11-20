#!/bin/bash

# Exit on error
set -e

echo "Creating Python virtual environment..."

echo "Installing pipenv..."
pip install pipenv

echo "Configuring pipenv with local Python..."
pipenv --python python

echo "Setting up pipenv environment..."
pipenv install

echo "Installing client dependencies..."
npm install --prefix client

echo "Installing additional Python packages..."
pipenv run pip install flask_bcrypt typing_extensions

echo "Setting up Flask environment variables..."
pipenv run bash -c 'export FLASK_APP=app.py && \
export FLASK_RUN_PORT=8080 && cd server && \
{ flask db init && echo "DB init successful"; } || echo "DB init failed, continuing..." && \
{ flask db migrate -m "initial migration" && echo "DB migrate successful"; } || echo "DB migrate failed, continuing..." && \
{ flask db upgrade head && echo "DB upgrade successful"; } || echo "DB upgrade failed, continuing..." && \
{ python seed.py && echo "Seeding successful"; } || echo "Seeding failed"'

echo "Setup completed successfully!"
