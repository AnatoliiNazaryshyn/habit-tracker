#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python3 manage.py migrate

# Create superuser if it doesn't exist
python3 manage.py makesuperuser

# Start the Django server
echo "Starting Django server..."
python3 manage.py runserver ${API_HOST}:8000
