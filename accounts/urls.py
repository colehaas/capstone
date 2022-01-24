"""
This module contains our mapping of URL path expressions to Django views for the "accounts" application.
"""
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

# URL namespace for this application.
app_name = 'accounts'

# URL patterns to be matched.
urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name="login"),
    path('logout/', LogoutView.as_view(template_name='accounts/login.html'), name='logout'),
    path('profile', views.profile, name='profile'),
    path('register', views.register, name='register'),
    path('applied', views.applied, name='applied'),
    path('review_apps', views.review_apps, name='review_apps'),
    path('disable_account', views.disable_account, name='disable_account'),
    path('sponsor_about_page_D', views.sponsor_about_page_D, name='sponsor_about_page_D'),
    path('sponsor_about_page_S', views.sponsor_about_page_S, name='sponsor_about_page_S'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('user_management', views.user_management, name='user_management'),
    path('delete_user/<int:value>', views.delete_user, name='delete_user'),
    path('sales_reports', views.sales_reports, name='sales_reports'),
    path('driver_sales', views.driver_sales, name='driver_sales'),
    path('order/<int:id>', views.order, name='order'),
    path('all_invoices', views.all_invoices, name='all_invoices'),
    path('invoice/<int:name>', views.invoice, name='invoice'),
    path('edit_user/<slug:role>/<int:value>', views.edit_user, name='edit_user'),
    path('create_user/<slug:value>', views.create_user, name='create_user'),
    path('swap_type', views.swap_type, name = 'swap_type'),
    path('edit_points/<int:value>', views.edit_points, name ='edit_points'),
    path('company_management', views.company_management, name='company_management'),
    path('edit_company/<int:value>', views.edit_company, name='edit_company'),
    path('delete_company/<int:value>', views.delete_company, name='delete_company'),
    path('point_change_logs', views.point_change_logs, name='point_change_logs'),
    path('login_logs', views.login_logs, name='login_logs'),
    path('application_logs', views.application_logs, name='application_logs'),
]
