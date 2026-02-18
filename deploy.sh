#!/bin/bash

# Deployment script for Django HRMS Portal to cPanel

echo "Starting deployment process..."

# 1. Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 2. Run migrations (for production database)
echo "Running database migrations..."
python manage.py migrate

# 3. Create superuser (optional - uncomment if needed)
# echo "Creating superuser..."
# python manage.py createsuperuser

echo "Deployment completed successfully!"
