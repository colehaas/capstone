"""
This module contains our Django views for the "accounts" application.
"""
from django.db.models.expressions import Exists
from catalog.models import CatalogFavorite
import pytz
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from datetime import datetime
from accounts.forms import UserInformationForm, EditUserInformationForm, EditAdminForm, EditSponsorForm, EditUserPointsForm, SponsorCompanyForm
from accounts.models import AuditLoginAttempt, UserInformation, AuditApplication, SponsorCompany, Points, Order, AuditPointChange


def login(request):
    """function login This function handles the view for the login page of the application.

    Args:
        request (HTTPRequest): A http request object created automatically by Django.

    Returns:
        HttpResponse: A generated http response object to the request.
    """
    return render(request, "accounts/login.html")


def logout(request):
    """function logout This function handles the view for the logout page of the application.

    Args:
        request (HTTPRequest): A http request object created automatically by Django.

    Returns:
        HttpResponse: A generated http response object to the request.
    """
    return redirect("/")


@login_required(login_url='/accounts/login/')
def profile(request):
    """function profile This function handles the view for the profile page of the application.

    Args:
        request (HTTPRequest): A http request object created automatically by Django.

    Returns:
        HttpResponse: A generated http response object to the request.
    """

    # find user logging in created by django
    # find userinfo with that email, change user to ^that user
    # delete original user that was created by us with invitation
    if len(User.objects.filter(email=request.user.email)) > 1:
        print(User.objects.filter(email=request.user.email), "####################", request.user.username)
        my_users = User.objects.filter(email=request.user.email)
        for obj in my_users:
            if obj.id is not request.user.id:
                print(obj)
                temp_user_info = UserInformation.objects.get(user=obj)
                temp_user_info.user = request.user
                temp_user_info.save()
                obj.delete()

    # Query for user in the 'User' table
    user = User.objects.get(email=request.user.email)

    # Case 1: The user email exists in our user information table.
    if UserInformation.objects.filter(user=user).exists():
        user_info = UserInformation.objects.get(user=user)
        all_apps = AuditApplication.objects.filter(driver=user_info)
        print(all_apps)
        if request.method == 'POST':
            if request.POST.get('newcompany') is not None:

                current_points = Points.objects.get(user=user_info, sponsor=user_info.sponsor_company)
                current_points.points = user_info.points
                current_points.save()

                user_info.sponsor_company = SponsorCompany.objects.get(company_name=request.POST.get('newcompany'))
                user_info.points = Points.objects.get(user=user_info, sponsor=user_info.sponsor_company).points

        user_info.last_login = datetime.now()
        user_info.is_active = True
        user_info.save()

        login_entry = AuditLoginAttempt(attempt_time=datetime.now(), login_user=user_info, is_successful=True)
        login_entry.save()
        if user_info.role_name == 'driver' and not user_info.viewing:
            points = Points.objects.filter(user=user_info.id)[0]
            print(points)
            return render(request, "accounts/profile.html", {"apps": all_apps, "points": points})
        return render(request, "accounts/profile.html", {"apps": all_apps})
    # Case 2: The user doesn't have an entry in our user information table,
    #          we redirect to the register page
    return redirect("/accounts/register")


@login_required(login_url='/accounts/login/')
@csrf_protect
def register(request):
    """function register This function handles the view for the account register page of the application.

    Args:
        request (HTTPRequest): A http request object created automatically by Django.

    Returns:
        HttpResponse: A generated http response object to the request depending on whether or not
                      the user is authenticated.
    """
    # Query for user in the 'User' table
    user = User.objects.get(email=request.user.email)

    # Case 1: We have received a POST request with some data
    if request.method == 'POST':
        current_sponsor = None
        # Check to see if we are creating a new user information entry or updating an existing one
        if UserInformation.objects.filter(user=user).exists():
            current_sponsor = UserInformation.objects.get(user=user).sponsor_company
            form = UserInformationForm(request.POST, instance=UserInformation.objects.get(user=user))
        else:
            form = UserInformationForm(request.POST)
        # Case 1a: A valid user profile form
        if form.is_valid():
            # Since 'user' is a foreign key, we must store the queried entry from the 'User' table
            user_info = form.save(commit=False)

            if UserInformation.objects.filter(user=user).exists():
                for obj in UserInformation.objects.get(user=user).all_companies.all():
                    if SponsorCompany.objects.get(company_name=form.cleaned_data['sponsor_company']) == obj:
                        # messages.error(request, "Error: You already belong to this company")
                        error = "Error: You already applied to this company. Please choose a different company"
                        return render(request, "accounts/register.html", {'form': form, 'error': error})
            user_info.user = user
            user_info.sponsor_company = current_sponsor
            user_info.save()
            # Send confirmation email to new user
            msg = EmailMessage(
            'DriveRite Inc',
            '<h2>Thank you for signing up with DriveRite Inc</h2>\
            <h3>A sponsor will review your application and contact \
            you shortly. <br> </br> Sincerely, \
            <br> The DriveRite Team</h3>',
            'DriveRite',
            [user.email])
            msg.content_subtype = "html"
            # msg.send()

            print(form.cleaned_data['sponsor_company'])

            sponsor = SponsorCompany.objects.get(company_name=form.cleaned_data['sponsor_company'])
            audit_app = AuditApplication(submission_time=datetime.now(), sponsor_company=sponsor,
                                         driver=user_info, apply_status='pending',
                                         reject_reason='N/A')
            audit_app.save()

            request.session.set_expiry(0)
            return redirect("/accounts/applied")
        # Case 1b: Not a valid user profile form, render the register page with the current form
        else:
            return render(request, "accounts/register.html", {'form': form})
    # Case 2: We have received something other than a POST request
    else:
        # Case 2a: The user exists in our user information table.
        if UserInformation.objects.filter(user=user).exists():
            form = UserInformationForm(instance=UserInformation.objects.get(user=user),
                                       initial={'user_email': request.user.email})
        # Case 2b: The user email doesn't exist in our user information table.
        else:
            form = UserInformationForm(initial={'user_email': request.user.email, 'first_name': user.first_name})

        request.session.set_expiry(0)
        return render(request, "accounts/register.html", {'form': form})


@login_required(login_url='/accounts/login/')
def applied(request):
    """function logout This function handles the view for the logout page of the application.

    Args:
        request (HTTPRequest): A http request object created automatically by Django.

    Returns:
        HttpResponse: A generated http response object to the request.
    """
    return render(request, "accounts/applied.html")

@login_required(login_url='/accounts/login/')
def sponsor_about_page_D(request):
    """function logout This function handles the view for the logout page of the application.

    Args:
        request (HTTPRequest): A http request object created automatically by Django.

    Returns:
        HttpResponse: A generated http response object to the request.
    """
    return render(request, "accounts/sponsor_about_page_D.html")


@login_required(login_url='/accounts/login/')
def sponsor_about_page_S(request):
    """function logout This function handles the view for the logout page of the application.

    Args:
        request (HTTPRequest): A http request object created automatically by Django.

    Returns:
        HttpResponse: A generated http response object to the request.
    """
    return render(request, "accounts/sponsor_about_page_S.html")

@login_required(login_url='/accounts/login/')
def edit_profile(request):
    """function logout This function handles the view for the logout page of the application.

    Args:
        request (HTTPRequest): A http request object created automatically by Django.

    Returns:
        HttpResponse: A generated http response object to the request.
    """
    return render(request, "accounts/edit_profile.html")

@login_required(login_url='/accounts/login/')
def point_change_logs(request):

    if request.method == "POST":
        data = request.POST
        start = data['start'] + " 00:00:00.0+00:00"
        end = data['end'] + " 00:00:00.0+00:00"
        
    else: 
        start = "2021-01-01 00:00:00.0+00:00"
        end = "2021-12-31 00:00:00.0+00:00"

    current_user = UserInformation.objects.get(user=User.objects.get(email=request.user.email))

    if current_user.role_name == 'admin':
        pointChange = AuditPointChange.objects.all().order_by('-change_time')
    else:
        pointChange = AuditPointChange.objects.filter(sponsor_company=current_user.sponsor_company).order_by('-change_time')

    pointChange = pointChange.filter(change_time__range=[start, end])

    return render(request, "accounts/point_change_logs.html" , {'pointChange' : pointChange, 'start': start, 'end': end})

@login_required(login_url='/accounts/login/')
def login_logs(request):

    if request.method == "POST":
        data = request.POST
        start = data['start'] + " 00:00:00.0+00:00"
        end = data['end'] + " 00:00:00.0+00:00"
        
    else: 
        start = "2021-01-01 00:00:00.0+00:00"
        end = "2021-12-31 00:00:00.0+00:00"
        
    logins = AuditLoginAttempt.objects.filter(attempt_time__range=[start, end])

    return render(request, "accounts/login_logs.html" , {'logins' : logins, 'start': start, 'end': end})


@login_required(login_url='/accounts/login/')
def application_logs(request):
    if request.method == "POST":
        data = request.POST
        start = data['start'] + " 00:00:00.0+00:00"
        end = data['end'] + " 00:00:00.0+00:00"
        
    else: 
        start = "2021-01-01 00:00:00.0+00:00"
        end = "2021-12-31 00:00:00.0+00:00"
        
    applications = AuditApplication.objects.filter(submission_time__range=[start, end])

    return render(request, "accounts/application_logs.html" , {'applications' : applications, 'start': start, 'end': end})


@login_required(login_url='/accounts/login/')
def review_apps(request):
    """function logout This function handles the view for the logout page of the application.

    Args:
        request (HTTPRequest): A http request object created automatically by Django.

    Returns:
        HttpResponse: A generated http response object to the request.
    """
    current_user = UserInformation.objects.get(user=User.objects.get(email=request.user.email))

    if request.method == 'POST':
        if request.POST.get('approve') is not None:
            print("approving ", request.POST.get('user'))
            pending_user = UserInformation.objects.get(user=User.objects.get(email=request.POST.get('user')))
            pending_user.is_email_verified = True
            sponsor = SponsorCompany.objects.get(company_name=request.POST.get('sponsor'))
            existing_audit_app = AuditApplication.objects.get(driver=pending_user, sponsor_company=sponsor)
            pending_user.all_companies.add(sponsor)
            if pending_user.sponsor_company is not None:
                print(pending_user.sponsor_company)
                current_points = Points.objects.get(user=pending_user, sponsor=pending_user.sponsor_company)
                current_points.points = pending_user.points
                current_points.save()
            pending_user.sponsor_company = sponsor
            new_points = Points(user=pending_user, points=0, sponsor=sponsor)
            new_points.save()
            pending_user.points = new_points.points
            pending_user.save()

            if current_user.role_name == 'sponsor':
                existing_audit_app.submission_time = datetime.now()
                existing_audit_app.sponsor = current_user
                existing_audit_app.apply_status = 'accepted'
                existing_audit_app.reject_reason = request.POST.get('reason')
                existing_audit_app.save()
            else:
                existing_audit_app.submission_time = datetime.now()
                existing_audit_app.sponsor = current_user
                existing_audit_app.apply_status = 'accepted'
                existing_audit_app.reject_reason = request.POST.get('reason')
                existing_audit_app.save()

            # Send Approval email to new user
            msg = EmailMessage(
                'DriveRite Inc',
                '<h2>Your Account Has Been Approved</h2>\
                <h3>After reviewing your application, \
                you have been approved to begin using DriveRite. \
                You may now begin earning rewards!  \
                <br> </br> Sincerely, \
                <br> The DriveRite Team</h3>',
                'DriveRite',
                [pending_user.user.email])
            msg.content_subtype = "html"
            # msg.send()

        if request.POST.get('reject') is not None:
            print("rejecting ", request.POST.get('user'))
            pending_user = UserInformation.objects.get(user=User.objects.get(email=request.POST.get('user')))

            sponsor = SponsorCompany.objects.get(company_name=request.POST.get('sponsor'))
            existing_audit_app = AuditApplication.objects.get(driver=pending_user, sponsor_company=sponsor)

            if current_user.role_name == 'sponsor':
                existing_audit_app.submission_time = datetime.now()
                existing_audit_app.sponsor = current_user
                existing_audit_app.apply_status = 'rejected'
                existing_audit_app.reject_reason = request.POST.get('reason')
                existing_audit_app.save()
            else:
                existing_audit_app.submission_time = datetime.now()
                existing_audit_app.apply_status = 'rejected'
                existing_audit_app.reject_reason = request.POST.get('reason')
                existing_audit_app.save()

            pending_user.save()

            # Send Reject email to new user
            msg = EmailMessage(
                'DriveRite Inc',
                '<h2>Your Account Has Been Rejected</h2>\
                <h3>After reviewing your application, \
                unfortunately you have been denied. \
                Please reach out if you think there \
                has been a mistake!  \
                <br> </br> Sincerely, \
                <br> The DriveRite Team</h3>',
                'DriveRite',
                [pending_user.user.email])
            msg.content_subtype = "html"
            # msg.send()

    if current_user.role_name == 'sponsor':
        if AuditApplication.objects.filter(apply_status='pending').filter(sponsor_company=current_user.sponsor_company).all().exists():
            open_apps = AuditApplication.objects.filter(apply_status='pending').filter(sponsor_company=current_user.sponsor_company).all()
        else:
            open_apps = None
    else:
        open_apps = AuditApplication.objects.filter(apply_status='pending').all()
    sponsor_companies = SponsorCompany.objects.all()
    number_of_sponsors = len(sponsor_companies)
    return render(request, "accounts/review_apps.html", {'open_apps': open_apps, 'sponsors': sponsor_companies,
                                                         'number_of_sponsors': number_of_sponsors})

@login_required(login_url='/accounts/login/')
def disable_account(request):

    if request.method == 'POST':
        #Get user instance
        user = request.user
        #If post request includes "Disable", change is_active flag
        if request.POST.get("Disable"):
            user.is_active = False
            user.save()
            messages.success(request, 'Profile successfully disabled')
        #Otherwise redirect back to profile
        else:
            return redirect("/accounts/profile")

    return render(request, "accounts/disable_account.html")


@login_required(login_url='/accounts/login/')
def sales_reports(request):

    if request.method == "POST":
        data = request.POST
        start = data['start'] + " 00:00:00.0+00:00"
        end = data['end'] + " 00:00:00.0+00:00"
        
    else: 
        start = "2021-01-01 00:00:00.0+00:00"
        end = "2021-12-31 00:00:00.0+00:00"
        
    sales = Order.objects.exclude(order_status='inCart').all().filter(last_status_change__range=[start, end])
    sponsor_companies = SponsorCompany.objects.all()
    number_of_sponsors = len(sponsor_companies)

    total_dollars = 0
    total_sales = 0
    sales_per = []
    for company in sponsor_companies:
        count = 0
        dollars = 0
        for order in sales:
            if company == order.sponsor:
                count += 1
                total_sales += 1
                dollars += order.retail_at_order
                total_dollars += order.retail_at_order
        sales_per.append([company, count, dollars])

    newest_first = Order.objects.exclude(order_status='inCart').all().order_by('last_status_change').filter(last_status_change__range=[start, end])
    oldest_first = Order.objects.exclude(order_status='inCart').all().order_by('-last_status_change').filter(last_status_change__range=[start, end])

    return render(request, "accounts/sales_reports.html", {'sales': sales,
                                                          'sponsors': sponsor_companies,
                                                          'number_of_sponsors': number_of_sponsors,
                                                          'sales_per': sales_per,
                                                          'total_dollars': total_dollars,
                                                          'total_sales': total_sales,
                                                           'oldest_first': oldest_first,
                                                           'newest_first': newest_first,
                                                           'start': start, 'end': end})


@login_required(login_url='/accounts/login/')
def driver_sales(request):

    if request.method == "POST":
        data = request.POST
        start = data['start'] + " 00:00:00.0+00:00"
        end = data['end'] + " 00:00:00.0+00:00"
        
    else: 
        start = "2021-01-01 00:00:00.0+00:00"
        end = "2021-12-31 00:00:00.0+00:00"

    sales = Order.objects.exclude(order_status='inCart').all().filter(last_status_change__range=[start, end])
    drivers = UserInformation.objects.filter(role_name='driver').all()
    number_of_drivers = len(drivers)

    total_dollars = 0
    total_sales = 0
    sales_per = []
    for driver in drivers:
        count = 0
        dollars = 0
        for order in sales:
            if driver == order.ordering_driver:
                count += 1
                total_sales += 1
                dollars += order.retail_at_order
                total_dollars += order.retail_at_order
        sales_per.append([driver, count, dollars])

    newest_first = Order.objects.exclude(order_status='inCart').all().order_by('last_status_change').filter(last_status_change__range=[start, end])
    oldest_first = Order.objects.exclude(order_status='inCart').all().order_by('-last_status_change').filter(last_status_change__range=[start, end])



    return render(request, "accounts/driver_sales.html", {'sales': sales,
                                                      'drivers': drivers,
                                                      'number_of_drivers': number_of_drivers,
                                                      'sales_per': sales_per,
                                                      'total_dollars': total_dollars,
                                                      'total_sales': total_sales,
                                                           'oldest_first': oldest_first,
                                                           'newest_first': newest_first,
                                                           'start': start, 'end': end})


@login_required(login_url='/accounts/login/')
def order(request, id):
    order = Order.objects.get(pk=id)
    return render(request, "accounts/order.html", {'order': order})


@login_required(login_url='/accounts/login/')
def all_invoices(request):

    def Sort_Tuple(tup):

        # reverse = None (Sorts in Ascending order)
        # key is set to sort using second element of
        # sublist lambda has been used
        tup.sort(key=lambda x: x[5])
        return tup

    if request.method == "POST":
        data = request.POST
        start = data['start'] + " 00:00:00.0+00:00"
        end = data['end'] + " 00:00:00.0+00:00"
        
    else: 
        start = "2021-01-01 00:00:00.0+00:00"
        end = "2021-12-31 00:00:00.0+00:00"

    sales = Order.objects.exclude(order_status='inCart').all().filter(last_status_change__range=[start, end])
    sponsor_companies = SponsorCompany.objects.all()
    number_of_sponsors = len(sponsor_companies)

    total_dollars = 0
    total_sales = 0
    sales_per = []
    utc = pytz.UTC
    for company in sponsor_companies:
        count = 0
        dollars = 0
        points = 0
        last_update = utc.localize(datetime(2000, 1, 1))
        for order in sales:
            if company == order.sponsor:
                count += 1
                total_sales += 1
                dollars += order.retail_at_order
                total_dollars += order.retail_at_order
                points += order.points_at_order
                if last_update < order.last_status_change:
                    last_update = order.last_status_change
        sales_per.append([company, count, dollars, dollars*.01, points, last_update])

    newest_first = list(reversed(Sort_Tuple(sales_per)))
    oldest_first = Sort_Tuple(sales_per)

    return render(request, "accounts/all_invoices.html", {'sales': sales,
                                                           'sponsors': sponsor_companies,
                                                           'number_of_sponsors': number_of_sponsors,
                                                           'sales_per': sales_per,
                                                           'total_dollars': total_dollars,
                                                           'total_sales': total_sales,
                                                           'oldest_first': oldest_first,
                                                           'newest_first': newest_first,
                                                           'start': start, 'end': end})


@login_required(login_url='/accounts/login/')
def invoice(request, name):
    company = SponsorCompany.objects.filter(company_name=name)

    count = 0
    dollars = 0
    points = 0
    sales_per = []
    utc = pytz.UTC
    last_update = utc.localize(datetime(2000, 1, 1))
    print(name)
    sponsor = SponsorCompany.objects.get(pk=name)
    sales = Order.objects.exclude(order_status='inCart').filter(sponsor=sponsor).all()
    print(sales)

    for order in sales:
        count += 1
        dollars += order.retail_at_order
        points += order.points_at_order
        if last_update < order.last_status_change:
            last_update = order.last_status_change
    sales_per.append([count, dollars, dollars * .01, points, last_update])

    return render(request, "accounts/invoice.html", {'company': sponsor, 'sales': sales, 'count': count, 'last': last_update, 'dollars': dollars, 'points': points, 'due': dollars*.01})

@login_required(login_url='/accounts/login/')
def user_management(request):
    current_user = UserInformation.objects.get(user=User.objects.get(email=request.user.email))

    if current_user.role_name == 'admin':
        admin_users = UserInformation.objects.filter(role_name='admin').all()
        sponsor_users = UserInformation.objects.filter(role_name='sponsor').all()
        driver_users = Points.objects.all()
    else:
        admin_users = UserInformation.objects.filter(role_name='admin').all()
        sponsor_users = UserInformation.objects.filter(role_name='sponsor').filter(sponsor_company=current_user.sponsor_company).all()
        driver_users = Points.objects.filter(sponsor=current_user.sponsor_company).all()

    return render(request, "accounts/user_management.html", {'current_user' : current_user, 'admins': admin_users, 'sponsors' : sponsor_users, 'drivers' : driver_users})

@login_required(login_url='/accounts/login/')
def create_user(request, value):
    creatorUser = UserInformation.objects.get(user=request.user)
    newUserRole = value

    if request.method == 'POST':
        if (newUserRole == 'admin'):
            form = EditAdminForm(request.POST)
        if (newUserRole == 'sponsor'):
            form = EditSponsorForm(request.POST)
        if (newUserRole == 'driver'):
            form = EditUserInformationForm(request.POST)

        if form.is_valid():
            newUserInfo = form.save(commit=False)

            if (newUserRole == 'driver'):
                #driverSponsor = form.cleaned_data['all_companies'].first()
                #newUserInfo.sponsor_company = driverSponsor
                newUserInfo.role_name = 'driver'
                
            if (newUserRole == 'sponsor'):
                newUserInfo.type_to_revert_to = 'sponsor'
                newUserInfo.role_name = 'sponsor'

            if (newUserRole == 'admin'):
                newUserInfo.is_admin = True
                newUserInfo.type_to_revert_to = 'admin'
                newUserInfo.role_name = 'admin'

            newBaseUser = User(username=form.cleaned_data['user_email'] , email=form.cleaned_data['user_email'], first_name=newUserInfo.first_name, last_name=newUserInfo.last_name)
            newBaseUser.save()

            newUserInfo.user = newBaseUser
            newUserInfo.save()

            if (newUserRole == 'driver'):
                targetSponsor = form.cleaned_data['sponsor_company']
                allSponsors = form.cleaned_data['all_companies']

                validM2M = False

                for company in allSponsors:
                    if (company == targetSponsor):
                        validM2M = True
                        break
                
                if(validM2M == False):
                    allSponsorError = "Driver's All Companies List must include the Sponsor Dropdown choice."
                    print(allSponsorError)
                    render(request, "accounts/create_user.html", {'form': form, 'creator_user': creatorUser, 'new_user_role': newUserRole, 'error': form.errors})
                else:
                    for company in form.cleaned_data['all_companies'] :
                        newPointsObject = Points(user=newUserInfo, sponsor=company)
                        newPointsObject.save()
                    form.save_m2m()

            request.session.set_expiry(0)
            return redirect("/accounts/user_management")
        else:
            print(form.errors)
            render(request, "accounts/create_user.html", {'form': form, 'creator_user': creatorUser, 'new_user_role': newUserRole, 'error': form.errors})

    else:
        if (newUserRole == 'admin'):
            form = EditAdminForm()
        if (newUserRole == 'sponsor'):
            if (creatorUser.role_name == 'sponsor'):
                form = EditSponsorForm(initial={'sponsor_company': creatorUser.sponsor_company})
            else:
                form = EditSponsorForm()
        if (newUserRole == 'driver'):
            form = EditUserInformationForm()

        request.session.set_expiry(0)
        return render(request, "accounts/create_user.html", {'form': form, 'creator_user': creatorUser, 'new_user_role': newUserRole})

@login_required(login_url='/accounts/login/')
def edit_user(request, role, value):

    temp_user = UserInformation.objects.get(user=request.user)
    if temp_user.role_name == 'driver' and not temp_user.viewing:
        editingUser = Points.objects.get(id=value)
    else:
        editingUser = UserInformation.objects.get(user=request.user)

    if (role == 'driver'):
        print(value)
        editedUser = Points.objects.get(id=value)
    else:
        editedUser = UserInformation.objects.get(id=value)
        

    # Case 1: We have received a POST request with some data
    if request.method == 'POST':

        if (role == 'admin'):
            form = EditAdminForm(request.POST, instance=UserInformation.objects.get(id=value))
        if (role == 'sponsor'):
            form = EditSponsorForm(request.POST, instance=UserInformation.objects.get(id=value))
        if (role == 'driver'):
            form = EditUserInformationForm(request.POST, instance=UserInformation.objects.get(id=editedUser.user.id))

        # Case 1a: A valid user profile form
        if form.is_valid():
            user_info = form.save(commit=False)

            if(role == 'driver'):
                targetSponsor = form.cleaned_data['sponsor_company']
                allSponsors = form.cleaned_data['all_companies']

                allPoints = Points.objects.filter(user=editedUser.user.id).all()

                validM2M = False
                changePointsData = False
                differentCompanies = []

                for company in allSponsors:
                    if (company == targetSponsor):
                        validM2M = True

                if(validM2M == False):
                    allSponsorError = "Driver's All Companies List must include the Sponsor Dropdown choice."
                    print(allSponsorError)
                    return render(request, "accounts/edit_user.html", {'form': form, 'role': role, 'driver_user': editedUser, 'error' : allSponsorError})

                #Checks for incoming company which doesn't have a points object, creates
                for company in allSponsors:
                    for pointsObject in allPoints:
                        if (pointsObject.sponsor == company):
                            changePointsData = False
                            break
                        else:
                            changePointsData = True
                    if (changePointsData):
                        newPointsObject = Points(user=editedUser.user, sponsor=company)
                        newPointsObject.save()
                    changePointsData = False

                changePointsData = False
                allPoints = Points.objects.filter(user=editedUser.user.id).all()

                #Checks for existing points object which isn't part of incoming company list, deletes
                for pointsObject in allPoints:
                    for company in allSponsors:
                        if (company == pointsObject.sponsor):
                            changePointsData = False
                            break
                        else:
                            changePointsData = True
                    if (changePointsData):
                        oldPointsObject = allPoints.get(sponsor=company.id)
                        oldPointsObject.delete()
                    changePointsData = False

            user_info.save()
            form.save_m2m()

            request.session.set_expiry(0)
            if temp_user.role_name == 'driver' and not temp_user.viewing:
                return redirect("/accounts/profile")
            return redirect("/accounts/user_management")

        # Case 1b: Not a valid user profile form, render the register page with the current form
        else:
            print(form.errors)
            return render(request, "accounts/edit_user.html", {'form': form, 'role': role, 'driver_user': editedUser, 'error': form.errors})

    # Case 2: We have received something other than a POST request
    else:

        if (role == 'admin'):
            form = EditAdminForm(instance=UserInformation.objects.get(id=value),
                initial={'user_email': editedUser.user.email})
        
        if (role == 'sponsor'):
            if(editingUser.role_name == 'admin'):
                form = EditSponsorForm(instance=UserInformation.objects.get(id=value),
                    initial={'user_email': editedUser.user.email})
            if(editingUser.role_name == 'sponsor'):
                form = EditSponsorForm(instance=UserInformation.objects.get(id=value),
                    initial={'user_email': editedUser.user.email, 'sponsor_company': editingUser.sponsor_company})

        if (role == 'driver'):
            form = EditUserInformationForm(instance=UserInformation.objects.get(id=editedUser.user.id), 
                initial={'user_email': editedUser.user.user.email})

        request.session.set_expiry(0)
        return render(request, "accounts/edit_user.html", {'form': form, 'role': role, 'driver_user': editedUser, 'editing_user' : editingUser})

@login_required(login_url='/accounts/login/')
def delete_user(request, value):

    if (UserInformation.objects.filter(id=value).exists()):
        user = UserInformation.objects.get(id=value)
        user.delete()

    return redirect("/accounts/user_management")


@login_required(login_url='/accounts/login/')
def swap_type(request):
    if request.POST.get('swapToDriver'):
        user_info = UserInformation.objects.get(user=request.user)
        user_info.viewing = True
        user_info.type_to_revert_to = user_info.role_name
        if user_info.role_name == "admin":
            user_info.is_admin = True
        user_info.role_name = 'driver'
        user_info.points = 99999
        user_info.save()
    elif request.POST.get('swapBack'):
        user_info = UserInformation.objects.get(user=request.user)
        user_info.viewing = False
        user_info.role_name = user_info.type_to_revert_to
        user_info.points = 0
        if user_info.is_admin:
            user_info.role_name = 'admin'
            user_info.sponsor_company = None
            user_info.all_companies.clear()
        user_info.save()
    elif request.POST.get('swapToSponsor'):
        sponsorToBecome = SponsorCompany.objects.get(company_name=request.POST.get('sponsor'))
        user_info = UserInformation.objects.get(user=request.user)
        user_info.viewing = True
        user_info.is_admin = True
        user_info.type_to_revert_to = user_info.role_name
        user_info.sponsor_company = sponsorToBecome
        user_info.all_companies.add(sponsorToBecome)
        user_info.role_name = 'sponsor'
        user_info.save()

    return redirect("/accounts/profile")

@login_required(login_url='/accounts/login/')
def edit_points(request, value):
    editingUser = UserInformation.objects.get(user=request.user)
    editedUserPoints = Points.objects.get(id=value)

    # Case 1: We have received a POST request with some data
    if request.method == 'POST':

        form = EditUserPointsForm(request.POST)

        # Case 1a: A valid user profile form
        if form.is_valid():
            #user_points = form.save(commit=False)
            
            affectedDriver = UserInformation.objects.get(id=editedUserPoints.user.id)
            pointChange = form.cleaned_data['point_change']
            changeReason = form.cleaned_data['change_reason']

            editedUserPoints.points += pointChange
            editedUserPoints.save()

            affectedDriver.points += pointChange
            affectedDriver.save()

            pointsChange = AuditPointChange(change_time=datetime.now(), sponsor=editingUser, driver=affectedDriver, point_change=pointChange, change_reason=changeReason, sponsor_company=editedUserPoints.sponsor)
            pointsChange.save()

            request.session.set_expiry(0)
            return redirect("/accounts/user_management")

        # Case 1b: Not a valid user profile form, render the register page with the current form
        else:
            print(form.errors)
            return render(request, "accounts/edit_points.html", {'form': form, 'edited_user': editedUserPoints, 'editing_user' : editingUser})

    # Case 2: We have received something other than a POST request
    else:
        form = EditUserPointsForm()

        request.session.set_expiry(0)
        return render(request, "accounts/edit_points.html", {'form': form, 'edited_user': editedUserPoints, 'editing_user' : editingUser})

@login_required(login_url='/accounts/login/')
def company_management(request):
    current_user = UserInformation.objects.get(user=User.objects.get(email=request.user.email))

    if current_user.role_name == 'admin':
        companies = SponsorCompany.objects.all()
    else:
        companies = SponsorCompany.objects.filter(id=current_user.sponsor_company).first()

    return render(request, "accounts/company_management.html", {'current_user' : current_user, 'companies': companies})

@login_required(login_url='/accounts/login/')
@csrf_protect
def edit_company(request, value):

    if SponsorCompany.objects.filter(id=value).exists():
        company = SponsorCompany.objects.get(id=value)
    else:
        company = None

    if request.method == 'POST':
        # Check to see if we are creating a new sponsor company entry or updating an existing one
        if SponsorCompany.objects.filter(id=value).exists():
            form = SponsorCompanyForm(request.POST, instance=SponsorCompany.objects.get(id=value))
        else:
            form = SponsorCompanyForm(request.POST)

        # Case 1a: A valid company profile form
        if form.is_valid():
            company_info = form.save(commit=False)
                
            company_info.save()

            request.session.set_expiry(0)

            current_user = UserInformation.objects.get(user=User.objects.get(email=request.user.email))

            if current_user.role_name == 'admin':
                companies = SponsorCompany.objects.all()
            else:
                companies = SponsorCompany.objects.filter(id=current_user.sponsor_company).first()

            return render(request, "accounts/company_management.html", {'current_user' : current_user, 'companies': companies})
        # Case 1b: Not a valid company profile form, render the edit page with the current form
        else:
            return render(request, "accounts/edit_company.html", {'form': form})
    
    else: 
        # Case 2a: The company exists in our sponsor company table.
        if SponsorCompany.objects.filter(id=value).exists():
            form = SponsorCompanyForm(instance=SponsorCompany.objects.get(id=value))

        # Case 2b: The company doesn't exist in our sponsor company table.
        else:
            form = SponsorCompanyForm()
        
        request.session.set_expiry(0)
        return render(request, "accounts/edit_company.html", {'company': company, 'form': form})

@login_required(login_url='/accounts/login/')
def delete_company(request, value):

    if (SponsorCompany.objects.filter(id=value).exists()):
        company = SponsorCompany.objects.get(id=value)
        company.delete()

    current_user = UserInformation.objects.get(user=User.objects.get(email=request.user.email))

    if current_user.role_name == 'admin':
        companies = SponsorCompany.objects.all()
    else:
        companies = SponsorCompany.objects.filter(id=current_user.sponsor_company).first()

    return render(request, "accounts/company_management.html", {'current_user' : current_user, 'companies': companies})

