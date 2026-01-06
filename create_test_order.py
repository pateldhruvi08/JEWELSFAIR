
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelryshop.settings')
django.setup()

from django.contrib.auth.models import User
from store.models import Product, Address, Order

# Get a user (assuming 'admin' exists or create one)
try:
    user = User.objects.get(username='admin')
except User.DoesNotExist:
    user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')

# Get a product
product = Product.objects.first()

# Get an address
address = Address.objects.filter(user=user).first()
if not address:
    address = Address.objects.create(user=user, locality='Test Locality', city='Test City', state='Test State')

# Create a Pending Order
order = Order.objects.create(
    user=user,
    address=address,
    product=product,
    quantity=1,
    status='Pending'
)

print(f"Created Pending Order ID: {order.id}")
