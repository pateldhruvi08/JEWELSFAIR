
import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelryshop.settings')
django.setup()

from store.models import Category

# 1. Fix Typo
try:
    rings = Category.objects.filter(title='RIngs').first()
    if rings:
        rings.title = 'Rings'
        rings.slug = 'rings'
        rings.save()
        print("Fixed RIngs typo.")
except Exception as e:
    print(e)

# 2. Add/Update Categories
categories_data = [
    {
        "title": "Earrings",
        "slug": "earrings",
        "image_path": "C:/Users/Admin/.gemini/antigravity/brain/31f0c78c-7edf-403b-84c4-6890c4a8ee9f/cat_earrings_1767177972813.png"
    },
    {
        "title": "Pendants",
        "slug": "pendants",
        "image_path": "C:/Users/Admin/.gemini/antigravity/brain/31f0c78c-7edf-403b-84c4-6890c4a8ee9f/cat_pendants_1767178011225.png"
    },
    {
        "title": "Anklets",
        "slug": "anklets",
        "image_path": "C:/Users/Admin/.gemini/antigravity/brain/31f0c78c-7edf-403b-84c4-6890c4a8ee9f/cat_anklets_1767178046208.png"
    }
]

for cat_data in categories_data:
    # Use defaults to satisfy NOT NULL constraints during creation
    cat, created = Category.objects.get_or_create(
        title=cat_data['title'],
        defaults={
            'slug': cat_data['slug'],
            'is_active': True,
            'is_featured': True
        }
    )
    
    # Update explicitly if it already existed or just created to be sure
    cat.slug = cat_data['slug']
    cat.is_active = True
    cat.is_featured = True
    
    if os.path.exists(cat_data['image_path']):
        # Only check if we need to update image (simplified: just update it)
        with open(cat_data['image_path'], 'rb') as f:
            cat.category_image.save(os.path.basename(cat_data['image_path']), File(f), save=False)
    
    cat.save()
    print(f"{'Created' if created else 'Updated'} category: {cat.title}")

# 3. Ensure other key categories are featured
for title in ['Gifts', 'Watches', 'Bracelets', 'Necklaces', 'Rings']:
    try:
        c = Category.objects.filter(title__iexact=title).first()
        if c:
            c.is_featured = True
            c.save()
            print(f"Ensured {c.title} is featured.")
        else:
             print(f"Category {title} not found (might be case sensitivity in DB, check manually).")
    except Exception as e:
        print(f"Error updating {title}: {e}")

print("Category setup complete.")
