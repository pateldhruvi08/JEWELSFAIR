
import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelryshop.settings')
django.setup()

from store.models import Category, Product

products_data = [
    {
        "category_title": "Anklets",
        "title": "Golden Heart Charm Anklet",
        "slug": "golden-heart-charm-anklet",
        "sku": "ANK-001",
        "price": 4500.00,
        "detail_description": "A dainty gold anklet featuring delicate heart charms. Perfect for adding a touch of romance to your summer style.",
        "image_path": "C:/Users/Admin/.gemini/antigravity/brain/31f0c78c-7edf-403b-84c4-6890c4a8ee9f/anklet_gold_heart_1767178889840.png"
    },
    {
        "category_title": "Anklets",
        "title": "Boho Pearl Layered Anklet",
        "slug": "boho-pearl-layered-anklet",
        "sku": "ANK-002",
        "price": 3200.00,
        "detail_description": "Chic silver layered anklet adorned with small freshwater pearls. A bohemian essential.",
        "image_path": "C:/Users/Admin/.gemini/antigravity/brain/31f0c78c-7edf-403b-84c4-6890c4a8ee9f/anklet_silver_pearl_1767178915429.png"
    },
    {
        "category_title": "Pendants",
        "title": "Classic Diamond Solitaire Pendant",
        "slug": "classic-diamond-solitaire-pendant",
        "sku": "PND-001",
        "price": 25000.00,
        "detail_description": "Timeless elegance defined. A single brilliant-cut diamond set in 18k gold.",
        "image_path": "C:/Users/Admin/.gemini/antigravity/brain/31f0c78c-7edf-403b-84c4-6890c4a8ee9f/pendant_diamond_solitaire_1767178940560.png"
    },
    {
        "category_title": "Pendants",
        "title": "Royal Sapphire Halo Pendant",
        "slug": "royal-sapphire-halo-pendant",
        "sku": "PND-002",
        "price": 35000.00,
        "detail_description": "A stunning deep blue sapphire surrounded by a halo of sparkling diamonds on a platinum chain.",
        "image_path": "C:/Users/Admin/.gemini/antigravity/brain/31f0c78c-7edf-403b-84c4-6890c4a8ee9f/pendant_sapphire_halo_1767178966824.png"
    }
]

for p_data in products_data:
    try:
        category = Category.objects.get(title__iexact=p_data['category_title'])
        product, created = Product.objects.get_or_create(
            title=p_data['title'],
            defaults={
                'slug': p_data['slug'],
                'sku': p_data['sku'],
                'short_description': p_data['detail_description'],
                'detail_description': p_data['detail_description'],
                'price': p_data['price'],
                'category': category,
                'is_active': True,
                'is_featured': True
            }
        )
        
        if created or not product.product_image:
            if os.path.exists(p_data['image_path']):
                with open(p_data['image_path'], 'rb') as f:
                    product.product_image.save(os.path.basename(p_data['image_path']), File(f), save=True)
                print(f"Added image to {product.title}")
            else:
                print(f"Image not found: {p_data['image_path']}")
        
        print(f"{'Created' if created else 'Updated'} product: {product.title}")

    except Category.DoesNotExist:
        print(f"Category {p_data['category_title']} not found.")
    except Exception as e:
        print(f"Error processing {p_data['title']}: {e}")

print("Product addition complete.")
