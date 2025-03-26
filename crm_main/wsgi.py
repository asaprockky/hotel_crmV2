import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_main.settings')

# Vercel requires a named 'app' variable
app = get_wsgi_application()