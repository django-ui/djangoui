#!/bin/bash

echo "Setting up Application..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
echo ""

# Install/Update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""

# Run migrations
echo "Running database migrations..."
python manage.py migrate
echo ""

echo ""
echo "You need to run this only once"
echo "Now run the application run.sh"