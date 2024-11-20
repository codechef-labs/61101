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

echo "Setup completed successfully!"
