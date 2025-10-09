#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Node dependencies and build Tailwind CSS
echo "Building Tailwind CSS..."
npm install
npm run build

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"