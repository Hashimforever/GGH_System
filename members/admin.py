from django.contrib import admin
from .models import *

# Register models dynamically if needed, or explicitly
import django.apps
app_config = django.apps.apps.get_app_config('members')
for model in app_config.get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
