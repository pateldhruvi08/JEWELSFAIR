import os,sys,traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE','jewelryshop.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
User=get_user_model()
user=User.objects.first()
print('Using user:', user)
client=Client()
if user:
    client.force_login(user)
client.raise_request_exception = True
try:
    r = client.get('/cart/')
    print('Status code:', r.status_code)
    print('Response length:', len(r.content))
    print(r.content.decode('utf-8')[:2000])
except Exception:
    traceback.print_exc()
    sys.exit(1)
