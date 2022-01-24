from django.contrib import admin

from django.contrib import admin
from .models import CatalogFavorite, CatalogItem, CatalogItemImage, SponsorCatalogItem, ItemReview, CatalogFavorite

# Register your models here. 
admin.site.register(CatalogItem)
admin.site.register(CatalogItemImage)
admin.site.register(SponsorCatalogItem)
admin.site.register(ItemReview)
admin.site.register(CatalogFavorite)