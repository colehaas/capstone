from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db.models.constraints import UniqueConstraint
from django.db.models.deletion import CASCADE, SET_NULL
from django.db.models.fields import DateTimeField
from django.utils import timezone
import datetime

#import accounts.models

class CatalogItem(models.Model):
    """
    Model of a particular catalog item.
    """
    item_name = models.CharField("Item Name", max_length=256, validators=[MinLengthValidator(1)], null=True)
    item_description = models.TextField("Item Description", validators=[MinLengthValidator(1)], null=True)
    retail_price = models.FloatField("Retail Price (MSRP)", null=True, validators=[MinValueValidator(0.01)])
    is_available = models.BooleanField("Item is Available From Retail", default=False)
    last_modified = models.IntegerField("Epoch time of Last Update to Item", validators=[MinValueValidator(1)], null=True)
    last_updated = models.DateTimeField("DateTime of the Last Update to Item", default=timezone.now)
    api_item_Id = models.CharField("API Link/Identifier", max_length=256, validators=[MinLengthValidator(1)], unique=True)


class CatalogItemImage(models.Model):
    """
    Model of a particular image belonging to a particular catalog item.
    """
    catalog_item = models.ForeignKey(CatalogItem, related_name='images', on_delete=CASCADE)
    image_link = models.URLField("Static Image Link")
    big_image_link = models.URLField("Static Image Link")

class SponsorCatalogItem(models.Model):
    """
    Model of a sponsor's particular catalog item, which may be made available to their drivers.
    """
    catalog_item = models.ForeignKey(CatalogItem, on_delete=CASCADE)
    sponsor_company = models.ForeignKey("accounts.SponsorCompany", on_delete=CASCADE)
    point_value = models.IntegerField("Driver Point Value", validators=[MinValueValidator(1)])
    date_added = models.DateTimeField("DateTime of the Date Added to Sponsor Catalog", default=timezone.now)
    is_available_to_drivers = models.BooleanField("Is Item Available For Driver Redemption", default=False)
    qty_in_cart = models.IntegerField("Number of  in users Cart", null=True, default=0)


class ItemReview(models.Model):
    """
    Model of an item review
    """
    catalog_item = models.ForeignKey(CatalogItem, on_delete=CASCADE, null=True)
    reviewer = models.ForeignKey("accounts.UserInformation", on_delete=SET_NULL, null=True)
    title = models.CharField("Title of the review", max_length=100,validators=[MinLengthValidator(3)], null=True)
    review = models.TextField("Text for review", validators=[MinLengthValidator(25)], null=True)
    likes =  models.PositiveIntegerField("Number of likes for a review", null=True, default=0)
    dislikes =  models.PositiveIntegerField("Number of dislikes for a review", null=True, default=0)
    when = DateTimeField("time post was created", auto_now_add=True)
    is_approved = models.BooleanField("Review has been approved by sponsor", default=False)
    has_reviewed = models.BooleanField("This field should probably be deleted", default=False)

class CatalogFavorite(models.Model):
    """
    Model of a favorited catalog item
    """
    catalog_item = catalog_item = models.ForeignKey(CatalogItem, on_delete=CASCADE, null=True)
    user = models.ForeignKey("accounts.UserInformation", on_delete=CASCADE, null=True)
    has_favorited = models.BooleanField("Has user favorited item", default=False)