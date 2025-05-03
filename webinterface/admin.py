from django.contrib import admin
from .models import Asset, Checkout

# Make the Asset and Checkout models editable in the bultin admin console
admin.site.register(Asset)
admin.site.register(Checkout)