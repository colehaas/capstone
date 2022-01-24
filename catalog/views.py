from django.shortcuts import render
from django.conf import settings
from accounts.models import SponsorCompany, UserInformation, Order
from catalog.models import CatalogItem, SponsorCatalogItem, CatalogItemImage, ItemReview, CatalogFavorite
from catalog.serializers import ItemSerializer, SponsorCatalogItemSerializer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import filters
from rest_framework import generics
from django.utils import timezone
from.forms import ItemReviewForm
import json
import requests 

# Create your views here.

base_url = settings.ETSY_BASE_URL
key = settings.ETSY_API_KEY

# Driver view
def shop(request):      
    user = UserInformation.objects.get(user=request.user)
    company = user.sponsor_company

    if SponsorCatalogItem.objects.filter(sponsor_company=company).exists():
        most_recent_update = SponsorCatalogItem.objects.order_by('date_added').first().date_added
        context = {'last_update' : most_recent_update}
        return render(request, "catalog/shop.html", context=context)
    #else
    return render(request, "catalog/shop.html")

# Sponsor view
def browse(request):

    if request.method == 'POST':
        add_ID = json.load(request)['ID']

        #add new instance catalog item
        if not CatalogItem.objects.filter(api_item_Id=add_ID).exists():
            url = base_url + '/listings/{}?includes=Images&api_key={}'.format(add_ID, key)
            response = requests.request("GET", url)
            search_was_successful = (response.status_code == 200)
            data = response.json()
            listing_data = data['results'][0]
            
            listing = CatalogItem.objects.create(api_item_Id=add_ID)

            
            listing.last_updated = timezone.now()
            listing.last_modified = listing_data['last_modified_tsz']
            # check if the modfied time has been changed 
            listing.item_name = listing_data['title']
            listing.item_description = listing_data['description']
            # ignore foreign currency for now
            listing.retail_price = float(listing_data['price'])
            if listing_data['state'] == "active":
                listing.is_available = True
            else:
                listing.is_available = False
            listing.save()

            images = listing_data['Images']
            for image in images:
                CatalogItemImage.objects.create(catalog_item = listing, image_link = image['url_170x135'], big_image_link = image['url_570xN'] )

                #if image['rank'] == 1:
                    #main_image = image['url_170x135']
            #CatalogItemImage.objects.create(catalog_item = listing, image_link = main_image)


        user = UserInformation.objects.get(user=request.user)
        if user.role_name == 'sponsor':
            company = user.sponsor_company
        else:
            company = user.sponsor_company
        catalog_item = CatalogItem.objects.filter(api_item_Id=add_ID)[0]

        # check not already in sponsor
        if not SponsorCatalogItem.objects.filter(sponsor_company=company, catalog_item=catalog_item).exists():
            # calculate points
            ratio = company.company_point_ratio 
            cents = round(catalog_item.retail_price * 100)
            points = (int)(cents/ratio)

            # create new sponspor item and add to database
            new_sponsor_item = SponsorCatalogItem(sponsor_company=company, catalog_item=catalog_item, point_value=points, is_available_to_drivers=True)
            new_sponsor_item.save()

        else:
            SponsorCatalogItem.objects.filter(sponsor_company=company, catalog_item=catalog_item).delete()
            
        return JsonResponse({'success' : 'sucess'})

    else:
        if CatalogItem.objects.all().exists():
            most_recent_update = CatalogItem.objects.order_by('last_updated').first().last_updated
            context = {'last_update' : most_recent_update}
            return render(request, "catalog/browse.html", context=context)
        #else
        return render(request, "catalog/browse.html")


def my_catalog(request):
    user = UserInformation.objects.get(user=request.user)
    if user.role_name == 'sponsor':
        company = user.sponsor_company
    else:
        company = user.sponsor_company
    items = CatalogItem.objects.filter(sponsorcatalogitem__in=SponsorCatalogItem.objects.filter(sponsor_company=company)).order_by('pk')
    sponsors = SponsorCatalogItem.objects.filter(catalog_item__in=items).order_by('catalog_item')
    images = CatalogItemImage.objects.filter(catalog_item__in=items).order_by('catalog_item')
    listings = zip(items, sponsors, images)
    return render(request, "catalog/my-catalog.html", context = {'listings' : listings})

# trying to use django-restframework & django-filters 
class Get_Items(generics.ListAPIView):
        queryset = CatalogItem.objects.all()
        serializer_class = ItemSerializer
        filter_backends = [filters.SearchFilter, filters.OrderingFilter]
        ordering_fields = ['last_modified', 'retail_price']
        search_fields = ['item_name', 'item_description']

class SponsorCompanyBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        company = UserInformation.objects.filter(user=self.request.user).sponsor_company
        return queryset.filter(sponsor_company=company)

class Get_Sponsor_Items(generics.ListCreateAPIView):
    
    def get_queryset(self):
        user = UserInformation.objects.get(user=self.request.user)
        if user.role_name == 'sponsor':
            company = user.sponsor_company
        else:
            company = user.sponsor_company
        return SponsorCatalogItem.objects.filter(sponsor_company=company)

    serializer_class = SponsorCatalogItemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['date_added', 'point_value']
    search_fields = ['catalog_item__item_name', 'catalog_item__item_description']


def all_items(request):
    if request.method == 'POST':
        data = json.load(request)
        add_ID = data['ID']
        price = data['price']
        
        user = UserInformation.objects.get(user=request.user)
        if user.role_name == 'sponsor':
            company = user.sponsor_company
        else:
            company = user.sponsor_company
        
        ratio = company.company_point_ratio 
        cents = round(price * 100)
        points = (int)(cents/ratio)
        if CatalogItem.objects.filter(api_item_Id=add_ID).exists():
            catalog_item = CatalogItem.objects.filter(api_item_Id=add_ID)[0]
            
            if SponsorCatalogItem.objects.filter(sponsor_company=company, catalog_item=catalog_item).exists():
                return JsonResponse({'inSponsor' : False, 'points': points})
            else:
                return JsonResponse({'inSponsor' : True, 'points': points})
        else:
            return JsonResponse({'inSponsor' : True, 'points': points})


@login_required(login_url='/accounts/login')
def product_page(request, id):
    user = UserInformation.objects.get(user=request.user)
    item = CatalogItem.objects.get(api_item_Id = id)
    if CatalogFavorite.objects.filter(catalog_item=item, user=user, has_favorited=True).exists():
        fave = CatalogFavorite.objects.get(catalog_item=item, user=user)
    else:
        fave = None
    #If user hasn't left a review for this item before
    if not ItemReview.objects.filter(catalog_item=item, reviewer=user).exists():
        #If user is submitting review
        if request.method == 'POST':
            r = ItemReview.objects.create(catalog_item=item,reviewer=user)
            r.save()
            form = ItemReviewForm(request.POST)
            if form.is_valid():
                r.title = form.cleaned_data['title']
                r.review = form.cleaned_data['review']
                r.has_reviewed = True
                r.is_approved = False
                r.save()
                form = None
        #otherwise display review form
        else:
            form = ItemReviewForm()
    else:
        form = None

    #Get associated product information
    items = CatalogItem.objects.filter(api_item_Id = id)
    sponsors = SponsorCatalogItem.objects.filter(catalog_item__in=items)
    images = CatalogItemImage.objects.filter(catalog_item__in=items)
    item = CatalogItem.objects.get(api_item_Id=id)
    reviews = ItemReview.objects.filter(catalog_item=item, is_approved=True)    
    reviewlist = []

    #creating list of review objects    
    for review in reviews.iterator():
        reviewlist.append(review)
    points = user.points
    listings = zip(items, sponsors)
    return render(request, "catalog/product_page.html", context = {'listings' : listings, 'images': images, 'points': points, 'reviewlist': reviewlist, 'form': form, 'fave':fave})    
        

@login_required(login_url='/accounts/login/')
def add_item_to_cart(request, id):
    
    #get user and associate them with an order
    user = UserInformation.objects.get(user=request.user)
    sponsor = user.sponsor_company
    item = CatalogItem.objects.get(api_item_Id=id)
    sponsor_item = SponsorCatalogItem.objects.get(catalog_item=item, sponsor_company = sponsor)
    if (sponsor_item.point_value < user.points):
        #edit: I don't think this is necessarily the users sponsor company
        

        #if item is in the cart already, change qty
        if Order.objects.filter(sponsor_catalog_item = sponsor_item, ordering_driver = user, sponsor = sponsor, order_status='inCart').exists():
            user.item_count = user.item_count + 1
            sponsor_item.qty_in_cart = sponsor_item.qty_in_cart + 1
            user.save()
            sponsor_item.save()
            return product_page(request,id)
        
        
        #else add item to order list
        order,created = Order.objects.get_or_create(ordering_driver=user, sponsor_catalog_item = sponsor_item, sponsor = sponsor, order_status='inCart')
        sponsor_item.qty_in_cart = 1
        user.item_count = user.item_count + 1
        user.save()
        sponsor_item.save()
        order.save()


    return product_page(request,id)



@login_required(login_url='/accounts/login/')
def my_cart(request):
    #Get user and order information
    user = UserInformation.objects.get(user=request.user)
    if Order.objects.filter(ordering_driver=user, order_status='inCart').exists():
        orders = Order.objects.filter(ordering_driver=user, order_status='inCart')
        items = []
        order = []
        images = []
        totals_dic = {
            "points": 0,
            "retail": 0
        }
        #Add active orders/images to list and calculate totals
        for obj in orders.iterator():
            items.append(obj.sponsor_catalog_item)
            numitems = obj.sponsor_catalog_item.qty_in_cart
            obj.points_at_order = obj.sponsor_catalog_item.point_value
            obj.retail_at_order =  obj.sponsor_catalog_item.catalog_item.retail_price
            image = CatalogItemImage.objects.filter(catalog_item=obj.sponsor_catalog_item.catalog_item).first()
            obj.save()
            order.append(obj)
            images.append(image)
            for i in range(numitems):
                totals_dic["points"] += obj.points_at_order
                totals_dic["retail"] += obj.retail_at_order                        
        item_list = zip(items, images)
    else:
        item_list = None
        order = None
        totals_dic = None

    return render(request, "catalog/my_cart.html", context = {'item_list': item_list, 'order': order, 'totals_dic': totals_dic})

def remove_item_from_cart(request, id):

    user = UserInformation.objects.get(user=request.user)
    sponsor = user.sponsor_company
    old_item = CatalogItem.objects.get(api_item_Id=id)
    sponsor_item = SponsorCatalogItem.objects.get(catalog_item=old_item, sponsor_company=sponsor)
    order = Order.objects.get(ordering_driver=user, sponsor=sponsor_item.sponsor_company, sponsor_catalog_item=sponsor_item, order_status='inCart')
    if order.sponsor_catalog_item.qty_in_cart > 1:
        user.item_count = user.item_count-1
        order.sponsor_catalog_item.qty_in_cart = order.sponsor_catalog_item.qty_in_cart - 1
        order.sponsor_catalog_item.save()
        user.save()
    else:
        user.item_count = user.item_count-1
        order.sponsor_catalog_item.qty_in_cart = order.sponsor_catalog_item.qty_in_cart-1
        order.sponsor_catalog_item.delete()
        order.sponsor_catalog_item.save()
        order.delete()
        user.save()
    
    return my_cart(request)

def add_item_from_cart_page(request, id):

    user = UserInformation.objects.get(user=request.user)
    sponsor = user.sponsor_company
    old_item = CatalogItem.objects.get(api_item_Id=id)
    sponsor_item = SponsorCatalogItem.objects.get(catalog_item=old_item, sponsor_company = sponsor)
    order = Order.objects.get(ordering_driver=user, sponsor=sponsor_item.sponsor_company, sponsor_catalog_item=sponsor_item, order_status='inCart')
    user.item_count = user.item_count + 1
    order.sponsor_catalog_item.qty_in_cart = order.sponsor_catalog_item.qty_in_cart + 1
    user.save()
    order.sponsor_catalog_item.save()


    return my_cart(request)

@login_required(login_url="/accounts/login")
def browse_pending_product_reviews(request,id):
    user = UserInformation.objects.get(user=request.user)
    item = CatalogItem.objects.get(api_item_Id= id)
    if ItemReview.objects.filter(catalog_item=item, is_approved=False).exists():
        pending_reviews = ItemReview.objects.filter(catalog_item=item, is_approved=False)
        review_list = []
        for review in pending_reviews.iterator():
            review_list.append(review)
    else:
        review_list = None

    return render(request, "catalog/browse_pending_product_reviews.html", context = {'review_list': review_list})

@login_required(login_url="/accounts/login")
def approve_pending_product_reviews(request, id, user):
   
    if request.method == 'POST':
        item = CatalogItem.objects.get(api_item_Id = id)
        pending_reviewer = UserInformation.objects.get(id = user)
        review = ItemReview.objects.get(catalog_item=item, reviewer=pending_reviewer)
        if request.POST.get('approve') is not None:
            review.is_approved = True
            review.save()
        if request.POST.get('reject') is not None:
            review.delete()
    return browse_pending_product_reviews(request,id)

def driver_cart(request, value):
    adminUser = UserInformation.objects.get(user=request.user)
    driverUser = UserInformation.objects.get(id=value)

    shopping_cart = Order.objects.filter(ordering_driver=driverUser, order_status='inCart')

    return render(request, "catalog/driver_cart.html", context = {'shopping_cart': shopping_cart})

def checkout(request):
    user = UserInformation.objects.get(user=request.user)
    if user.role_name != 'sponsor' and user.type_to_revert_to != 'sponsor' and not user.is_admin:
        sponsor = user.sponsor_company
        orders = Order.objects.filter(ordering_driver=user, order_status='inCart')
        sponsor_items = SponsorCatalogItem.objects.filter(order__in = orders)
        for items in sponsor_items:
            items.qty_in_cart = 0
            items.save()
        for order in orders:
            #simulate shipping process
            order.order_status = 'delivered'
            order.last_status_change = timezone.now()
            order.save()
            user.points -= order.points_at_order
            user.item_count -= 1
            user.save()
        user.item_count = 0  
        user.save()
        
    return my_cart(request)

def order_history(request):
    user = UserInformation.objects.get(user=request.user)
    if Order.objects.filter(ordering_driver=user).exclude(order_status='inCart').exists():
        orders = Order.objects.filter(ordering_driver=user).exclude(order_status='inCart').order_by('-last_status_change')
        sponsors = SponsorCatalogItem.objects.filter(order__in=orders).order_by('-order__last_status_change')
        items = []
        images = []
        for sponsor in sponsors:
            item = sponsor.catalog_item
            items.append(item)
            image = CatalogItemImage.objects.filter(catalog_item=item).first()
            print(image)
            images.append(image)

        data = zip(orders, sponsors, items, images)

    else:
        data = None
    context = {'data' : data}
    return render(request, "catalog/order_history.html", context = context)

def update_item(id):
    listing = CatalogItem.objects.filter(api_item_Id=id)
    url = base_url + '/listings/{}?api_key={}'.format(listing.api_item_Id, key)
    response = requests.request("GET", url)
    search_was_successful = (response.status_code == 200)
    data = response.json()
    listing_data = data['results'][0]

    listing.last_updated = timezone.now()
    if not (listing_data['last_modified_tsz'] == listing.last_modified):
        listing.last_modified = listing_data['last_modified_tsz']
        # check if the modfied time has been changed 
        listing.item_name = listing_data['title']
        listing.item_description = listing_data['description']
        # ignore foreign currency for now
        listing.retail_price = float(listing_data['price'])
        if listing_data['state'] == "active":
            listing.is_available = True
        else:
            listing.is_available = False
        listing.save()

        # create new catalog item image instance if one doesnt exist
        if not CatalogItemImage.objects.filter(catalog_item = listing).exists():
            url = base_url + '/listings/{}/images?api_key={}'.format(listing.api_item_Id, key)
            response = requests.request("GET", url)
            search_was_successful = (response.status_code == 200)
            image_data = response.json()
            images = image_data['results']
            for image in images:
                if image['rank'] == 1:
                    main_image = image['url_170x135']
            CatalogItemImage.objects.create(catalog_item = listing, image_link = main_image)

@login_required(login_url="/accounts/login")
def favorite_item(request, id):
    item = CatalogItem.objects.get(api_item_Id=id)
    user = UserInformation.objects.get(user=request.user)
    # if object has been created already, modify has favorited value
    if CatalogFavorite.objects.filter(catalog_item=item, user=user).exists():
        fav = CatalogFavorite.objects.get(catalog_item=item, user=user)
        print("doing stuff")
        if fav.has_favorited == False:
            fav.has_favorited = True
        else:
            fav.has_favorited = False
        fav.save()
    else:
        CatalogFavorite.objects.create(catalog_item=item, user=user, has_favorited=True)

    return product_page(request,id)

def browse_favorites(request):
    user = UserInformation.objects.get(user=request.user)
    if CatalogFavorite.objects.filter(user=user, has_favorited=True).exists():
        favorite_items = CatalogFavorite.objects.filter(user = user, has_favorited=True)
        items = []
        images = []
        # for all favorited items get the image
        for item in favorite_items:
            items.append(item.catalog_item)
            image = CatalogItemImage.objects.filter(catalog_item=item.catalog_item).first()
            images.append(image)
        item_list = zip(items, images)
    else:
        item_list = None

    return render(request, "catalog/favorites.html", context = {'item_list':item_list})
