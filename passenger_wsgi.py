# import os
# import sys

# # Add the project directory to the Python path
# project_directory = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, project_directory)

# # Set the Django settings module
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms_portal.settings')

# # Import Django and set up the application
# import django
# from django.core.wsgi import get_wsgi_application

# django.setup()

# # Get the WSGI application
# application = get_wsgi_application()
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hrms_portal.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
