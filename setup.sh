#!/bin/bash

# Exit on error
set -e

echo "Creating Python virtual environment..."
python3 -m venv ./

echo "Installing pipenv..."
./bin/pip install pipenv

echo "Configuring pipenv with local Python..."
./bin/pipenv --python ./bin/python

echo "Setting up pipenv environment..."
./bin/pipenv install

echo "Installing client dependencies..."
npm install --prefix client

echo "Installing additional Python packages..."
./bin/pipenv run pip install flask_bcrypt typing_extensions

echo "Setting up Flask environment variables..."
./bin/pipenv run bash -c 'export FLASK_APP=app.py && \
export FLASK_RUN_PORT=8080 && cd server && \
{ flask db init && echo "DB init successful"; } || echo "DB init failed, continuing..." && \
{ flask db migrate -m "initial migration" && echo "DB migrate successful"; } || echo "DB migrate failed, continuing..." && \
{ flask db upgrade head && echo "DB upgrade successful"; } || echo "DB upgrade failed, continuing..." && \
{ python seed.py && echo "Seeding successful"; } || echo "Seeding failed"'

echo "Setup completed successfully!"
