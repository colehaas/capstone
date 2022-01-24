"""
This module contains our mapping of URL path expressions to Django views for the "catalog" application.
"""

from django.urls import path
from . import views

# URL namespace for this application.
app_name = 'catalog'

# URL patterns to be matched.
urlpatterns = [
    path('shop', views.shop, name='shop'),
    path('my_cart', views.my_cart, name='my_cart'),
    path('all_items', views.all_items, name='all_items'),
    path('items', views.Get_Items.as_view(), name = 'items'),
    path('sponsor-items', views.Get_Sponsor_Items.as_view(), name = 'sponsor-items'),
    path('browse', views.browse, name = 'browse'),
    path('product-page/<int:id>', views.product_page, name = 'product_page'),
    path('add_item/<int:id>/', views.add_item_to_cart, name = 'add_item_to_cart'),
    path('remove_item_from_cart/<int:id>/', views.remove_item_from_cart, name = 'remove_item_from_cart'),
    path('add_item_from_cart_page/<int:id>/', views.add_item_from_cart_page, name = 'add_item_from_cart_page'),
    path('driver_cart/<int:value>/', views.driver_cart, name='driver_cart'),
    path('browse_pending_product_reviews/<int:id>/', views.browse_pending_product_reviews, name= 'browse_pending_product_reviews'),
    path('approve_pending_product_reviews/<int:id>/<int:user>', views.approve_pending_product_reviews, name= 'approve_pending_product_reviews'),
    path('checkout', views.checkout, name = 'checkout'),
    path('order-history', views.order_history, name = 'order_history'),
    path('favorite_item/<int:id>/', views.favorite_item, name = 'favorite_item'),
    path('browse_favorites', views.browse_favorites, name = 'browse_favorites'),

]