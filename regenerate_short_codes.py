import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gift_platform.settings')
django.setup()

from core.models import BaseGift
from django.apps import apps

def regenerate_short_codes():
    """Regenerate short codes for gifts that contain special characters."""
    
    # Get all gift models from all apps
    gift_models = []
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            if issubclass(model, BaseGift) and model != BaseGift:
                gift_models.append(model)
    
    total_regenerated = 0
    
    for model in gift_models:
        app_name = model._meta.app_label
        print(f"\nChecking {app_name}...")
        
        # Find gifts with special characters in short_code
        gifts_with_special = model.objects.filter(short_code__regex=r'[!@#$%]')
        count = gifts_with_special.count()
        
        if count > 0:
            print(f"  Found {count} gifts with special characters")
            
            for gift in gifts_with_special:
                old_code = gift.short_code
                # Regenerate short code (will now be numeric-only)
                gift.short_code = None
                gift.save()
                new_code = gift.short_code
                print(f"    {gift.id}: {old_code} -> {new_code}")
                total_regenerated += 1
        else:
            print(f"  No gifts with special characters found")
    
    print(f"\nTotal regenerated: {total_regenerated}")

if __name__ == '__main__':
    regenerate_short_codes()
