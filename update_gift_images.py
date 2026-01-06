
import os
import django
import shutil
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelryshop.settings')
django.setup()

from store.models import Product

# Mapping of product slug to generated image path
image_map = {
    "luxury-diamond-gift-box": "C:/Users/Admin/.gemini/antigravity/brain/31f0c78c-7edf-403b-84c4-6890c4a8ee9f/luxury_diamond_gift_box_1767173754934.png",
    "gold-plated-rose": "C:/Users/Admin/.gemini/antigravity/brain/31f0c78c-7edf-403b-84c4-6890c4a8ee9f/gold_plated_rose_gift_1767173781446.png",
    "silver-couple-rings-set": "C:/Users/Admin/.gemini/antigravity/brain/31f0c78c-7edf-403b-84c4-6890c4a8ee9f/silver_couple_rings_1767173807615.png",
    "pearl-jewelry-set": "C:/Users/Admin/.gemini/antigravity/brain/31f0c78c-7edf-403b-84c4-6890c4a8ee9f/pearl_jewelry_set_1767173830939.png"
}

try:
    for slug, src_path in image_map.items():
        if os.path.exists(src_path):
            product = Product.objects.filter(slug=slug).first()
            if product:
                print(f"Updating image for {product.title}...")
                with open(src_path, 'rb') as f:
                    # Django's File object wrapper
                    django_file = File(f)
                    # We simply assign it. Django handles the saving to media root.
                    # We rename it nicely to match the product
                    filename = f"{slug}.png"
                    product.product_image.save(filename, django_file, save=True)
                print(f"Successfully updated {product.title}")
            else:
                print(f"Product not found: {slug}")
        else:
            print(f"Source file not found: {src_path}")

except Exception as e:
    print(f"Error: {e}")
