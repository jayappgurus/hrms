import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
import django
django.setup()
from django.db import connection

cursor = connection.cursor()
# Clear all migration history
cursor.execute('DELETE FROM django_migrations')
print('Cleared all migration history from database')
