
import os
import django
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelryshop.settings')
django.setup()

from store.models import Category, Product

def generate_sku():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

try:
    gift_cat = Category.objects.filter(title='Gifts').first()
    if not gift_cat:
        print("Gifts category does not exist. Creating it.")
        gift_cat = Category.objects.create(title='Gifts', slug='gifts', is_active=True, is_featured=True)
    
    print(f"Category: {gift_cat.title}")
    
    existing_count = Product.objects.filter(category=gift_cat).count()
    print(f"Current products in Gifts: {existing_count}")
    
    products_to_create = [
        {
            "title": "Luxury Diamond Gift Box",
            "slug": "luxury-diamond-gift-box",
            "short_description": "A perfect gift for your loved ones.",
            "detail_description": "This luxury gift box contains a set of premium diamond jewelry including a necklace and earrings. Perfect for anniversaries.",
            "price": 15000,
            "is_active": True,
            "is_featured": True,
            "sku": "GIFT-001"
        },
        {
            "title": "Gold Plated Rose",
            "slug": "gold-plated-rose",
            "short_description": "An everlasting rose for everlasting love.",
            "detail_description": "A real rose dipped in 24k gold, preserved to last forever. Comes in a beautiful display case.",
            "price": 2500,
            "is_active": True,
            "is_featured": True,
            "sku": "GIFT-002"
        },
        {
            "title": "Silver Couple Rings Set",
            "slug": "silver-couple-rings-set",
            "short_description": "Matching rings for couples.",
            "detail_description": "Sterling silver rings with adjustable size. Engraved with 'Forever Love'.",
            "price": 3500,
            "is_active": True,
            "is_featured": True,
            "sku": "GIFT-003"
        },
        {
            "title": "Pearl Jewelry Set",
            "slug": "pearl-jewelry-set",
            "short_description": "Classic pearls for a timeless look.",
            "detail_description": "Genuine freshwater pearls strung into a necklace and bracelet. A classy gift for her.",
            "price": 8000,
            "is_active": True,
            "is_featured": True,
            "sku": "GIFT-004"
        }
    ]
    
    for p_data in products_to_create:
        if not Product.objects.filter(slug=p_data['slug']).exists():
            # Check if SKU exists, if so, regenerate or skip
            if Product.objects.filter(sku=p_data['sku']).exists():
                 print(f"SKU {p_data['sku']} exists, skipping or regenerating...")
                 p_data['sku'] = "GIFT-" + generate_sku()
            
            Product.objects.create(category=gift_cat, **p_data)
            print(f"Created product: {p_data['title']}")
        else:
            print(f"Product already exists: {p_data['title']}")
            
    print("Finished adding products.")

except Exception as e:
    print(f"Error: {e}")
