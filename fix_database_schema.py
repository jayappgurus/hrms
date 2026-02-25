import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')
import django
django.setup()
from django.db import connection

cursor = connection.cursor()

# Add missing 'name' column to django_content_type table
try:
    cursor.execute('ALTER TABLE django_content_type ADD COLUMN name VARCHAR(100) NULL')
    print('Added name column to django_content_type table')
except Exception as e:
    print(f'Error adding name column: {e}')

# Check if the column exists now
cursor.execute('DESCRIBE django_content_type')
columns = cursor.fetchall()
print('Current columns in django_content_type:')
for column in columns:
    print(f'  {column[0]}')
