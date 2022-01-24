"""
This module contains model templates for the "accounts" application. When we create a new item in the database,
a new instance of a model will be made.
"""
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.db.models.deletion import CASCADE, SET_NULL
from django.db.models.fields import DateTimeField
import datetime

class SponsorCompany(models.Model):
    """
    Model of a sponsor company to keep track of info for sponsors' companies.
    """
    company_name = models.CharField("Company Name", max_length=25, validators=[MinLengthValidator(1)])
    company_phone_number = models.IntegerField("Phone Number", validators=[MinValueValidator(1000000000), MaxValueValidator(99999999999999)])
    company_street_address = models.CharField("Company Street Address", max_length=32, validators=[MinLengthValidator(1)])
    company_city = models.CharField("Company City", max_length=25, validators=[MinLengthValidator(1)])
    company_state = models.CharField("Company State", max_length=25, validators=[MinLengthValidator(1)])
    company_zipcode = models.IntegerField("Zip Code", validators=[MinValueValidator(500), MaxValueValidator(99999)])
    company_point_ratio = models.IntegerField("US Cents to Catalog Points Ratio", default=1)
    company_about_info = models.CharField("About sponsor", max_length=1000000, default="Enter about me info here")


    def __str__(self):
        """function __str__ is used to create a string representation of this class

        Returns:
            str: company name
        """
        return self.company_name

class UserInformation(models.Model):
    """
    Contains a model of a user to keep track of user information.
    """
    # All of the fields in the model has validators to make sure they are valid.
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Foreign key referring to an entry in the user table

    # Two-tuple for roles where item 1 is the field value, and item 2 is the display name
    ROLE_NAME_CHOICES = (
        ('driver', 'Driver'),
        ('sponsor', 'Sponsor'),
        ('admin', 'Admin')
    )

    STATES = (
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'),
        ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'),
        ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'),
        ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
        ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'),
        ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'),
        ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
        ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'),
        ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')
    )

    role_name = models.CharField("Role Name", max_length=25, choices=ROLE_NAME_CHOICES, default="driver", validators=[MinLengthValidator(1)])
    first_name = models.CharField("First Name", max_length=25, default="N/A", validators=[MinLengthValidator(1)])
    last_name = models.CharField("Last Name", max_length=25, default="N/A", validators=[MinLengthValidator(1)])
    phone_number = models.IntegerField("Phone Number", null=True, validators=[MinValueValidator(1000000000), MaxValueValidator(99999999999999)])
    last_login = models.DateTimeField("Last User Login", auto_now_add=True, blank=True)
    is_email_verified = models.BooleanField("If User Verified Email", default=False)
    is_active_account = models.BooleanField("If User Has Account Enabled", default=True)
    sponsor_company = models.ForeignKey(SponsorCompany, on_delete=models.CASCADE, null=True, blank=True, related_name="current_company")
    all_companies = models.ManyToManyField(SponsorCompany, blank=True, related_name="all_companies")
    points = models.IntegerField("Points", null=True, default=0)
    address = models.CharField("Address", max_length=100, default="N/A", blank=True)
    license_number = models.CharField("License", max_length=20, default="N/A", blank=True)
    state = models.CharField("State", choices=STATES, max_length=20, blank=True)
    item_count = models.IntegerField("Number of items in users Cart", null=True, default=0)
    viewing = models.BooleanField("Viewing Other User", default=False)
    type_to_revert_to = models.CharField("Type To Revert To", max_length=25, choices=ROLE_NAME_CHOICES, default="driver",
                                 validators=[MinLengthValidator(1)])
    is_admin = models.BooleanField("Is an Admin", default=False)

    def __str__(self):
        """function __str__ is used to create a string representation of this class

        Returns:
            str: user email
        """
        return self.first_name + " " + self.last_name

    def get_user_email(self):
        """function get_user_email is an helper function to retrieve the email associated with the user

        Returns:
            str: user email
        """
        return self.user.email

    get_user_email.short_description = 'User Email'  # Renames column head



class Order(models.Model):
    """
    Model of an order a driver may create (whether pending, completed, or otherwise).
    """
    # Two-tuple for roles where item 1 is the field value, and item 2 is the display name
    ORDER_STATUS_CHOICES = (
        ('inCart', 'In-Cart'),
        ('ordered', 'Ordered'),
        ('shipping', 'Shipping'),
        ('fulfilled', 'Fulfilled'),
        ('canceled', 'Canceled'),
        ('delivered', 'Delivered'),
        ('returnRequest', 'Return In-Progress'),
        ('returned', 'Returned')
    )

    sponsor_catalog_item = models.ForeignKey("catalog.SponsorCatalogItem", on_delete=SET_NULL, null=True,blank=True)
    sponsor = models.ForeignKey(SponsorCompany, on_delete=SET_NULL, null=True, blank=True)
    ordering_driver = models.ForeignKey(UserInformation, on_delete=SET_NULL, null=True)
    order_status = models.CharField("Order Status", max_length=25, choices=ORDER_STATUS_CHOICES)
    last_status_change = models.DateTimeField("Last DateTime of OrderStatus Update", default=datetime.datetime.utcnow)
    retail_at_order = models.FloatField("Retail Price (MSRP) at Order Time", null=True,
                                        validators=[MinValueValidator(0.01)])
    points_at_order = models.IntegerField("Driver Point Cost at Order Time", null=True,
                                          validators=[MinValueValidator(1)])


class AuditApplication(models.Model):
    """
    Model of a particular application being audited (regardless of application status).
    """
    APPLICATION_STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    )

    submission_time = models.DateTimeField("DateTime of Application Submission")
    # Associated to company so that any sponsor employee of company may approve/reject
    sponsor_company = models.ForeignKey(SponsorCompany, on_delete=CASCADE, null=True)
    # Approving/Rejecting Sponsor
    sponsor = models.ForeignKey(UserInformation, on_delete=SET_NULL, null=True, related_name="%(class)s_sponsor",
                                blank=True)
    driver = models.ForeignKey(UserInformation, on_delete=SET_NULL, null=True, related_name="%(class)s_driver")
    apply_status = models.CharField("Application Status", max_length=25, choices=APPLICATION_STATUS_CHOICES)
    reject_reason = models.CharField("Rejection Reason", max_length=128, blank=True)


class AuditPointChange(models.Model):
    """
    Model of a particular point change performed against a driver being audited.
    """
    change_time = models.DateTimeField("DateTime of Point Change", default=datetime.datetime.utcnow)
    # Approving/Rejecting Sponsor
    sponsor = models.ForeignKey(UserInformation, on_delete=SET_NULL, null=True, related_name="%(class)s_sponsor", blank=True)
    driver = models.ForeignKey(UserInformation, on_delete=CASCADE, null=True)
    point_change = models.IntegerField("Point Change for Driver")
    change_reason = models.CharField("Point Change Reason", max_length=128)
    sponsor_company = models.ForeignKey(SponsorCompany, on_delete=CASCADE, null=True)


class AuditLoginAttempt(models.Model):
    """
    Model of a particular login attempt being audited.
    """
    attempt_time = models.DateTimeField("DateTime of login attempt")
    login_user = models.ForeignKey(UserInformation, on_delete=CASCADE, null=True)
    is_successful = models.BooleanField("Whether a login attempt is successful", null=True)


class Points(models.Model):
    """
    Model of a Points.
    """
    user = models.ForeignKey(UserInformation, on_delete=models.CASCADE, null=True, blank=True, related_name="users_points")
    sponsor = models.ForeignKey(SponsorCompany, on_delete=models.CASCADE, null=True, blank=True)
    points = models.IntegerField("Driver Points", null=True, default=0)
