# kursov_proekt/asgi.py
import os
from django.core.asgi import get_asgi_application

# Указва на Django къде да търси настройките
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kursov_proekt.settings')

# Това е основната точка за приложение, която Daphne ще използва
application = get_asgi_application()
