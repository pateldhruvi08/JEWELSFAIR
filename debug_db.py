
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelryshop.settings')
django.setup()

from store.models import Category, Product

print("Checking Database Content...")
try:
    cats = Category.objects.all()
    print(f"Categories Count: {cats.count()}")
    for c in cats[:5]:
        print(f"Category: '{c.title}'")

    prods = Product.objects.all()
    print(f"Products Count: {prods.count()}")
    for p in prods[:5]:
        print(f"Product: '{p.title}'")

except Exception as e:
    print(f"Error: {e}")
