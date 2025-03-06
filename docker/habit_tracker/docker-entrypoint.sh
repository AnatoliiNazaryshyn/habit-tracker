#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python3 manage.py migrate

# Start the Django server
echo "Starting Django server..."
python3 manage.py runserver ${API_HOST}:8000
