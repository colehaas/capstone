from rest_framework import serializers
from accounts.models import SponsorCompany, UserInformation
from catalog.models import CatalogItem, SponsorCatalogItem, CatalogItemImage


class CatalogItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogItemImage
        fields = ['image_link']


class ItemSerializer(serializers.ModelSerializer):
    images = CatalogItemImageSerializer(many=True,read_only=True)
    
    class Meta:
        model = CatalogItem
        fields = ['item_name', 'item_description', 'retail_price', 'is_available', 'last_modified', 'api_item_Id', 'images']

class SponsorCatalogItemSerializer(serializers.ModelSerializer):
    sponsor_company = serializers.SlugRelatedField(read_only=True, slug_field='company_name')
    catalog_item = ItemSerializer(read_only = True)

    class Meta:
        model = SponsorCatalogItem
        fields = ['sponsor_company', 'point_value', 'date_added', 'is_available_to_drivers', 'catalog_item']

        
