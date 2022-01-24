"""
This module contains custom forms used to collect the information needed to create a model.
"""
from django import forms
from django.db.models.query import QuerySet
from .models import Points, UserInformation, SponsorCompany


class UserInformationForm(forms.ModelForm):
    """
    This form creates an instance of a UserInformation model and collects its fields
    """
    states = [
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
    ]

    # Fields that will need to be completed in this form
    user_email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'readonly': 'readonly'}))  # read only
    first_name = forms.CharField(label='First Name', max_length=25)
    last_name = forms.CharField(label='Last Name', max_length=25)
    phone_number = forms.IntegerField(label='Phone Number', max_value=9999999999, min_value=1000000000)
    sponsor_company = forms.ModelChoiceField(label='Sponsor', queryset=SponsorCompany.objects.all())
    address = forms.CharField(label='Address', max_length=100)
    license_number = forms.CharField(label='License', max_length=20)
    state = forms.ChoiceField(label='State', choices=states)

    def __init__(self, *args, **kwargs):
        """function __init__ is called to instantiate the user information form

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super(UserInformationForm, self).__init__(*args, **kwargs)

        # Validator that makes sure all the fields have been filled in
        for _field_name, field in self.fields.items():
            field.required = True

    class Meta:
        """
        A class that stores the meta information about this form
        """
        model = UserInformation
        fields = ['user_email', 'first_name', 'last_name', 'phone_number', 'sponsor_company', 'address', 'license_number', 'state']

class EditUserInformationForm(forms.ModelForm):
    """
    This form creates an instance of a UserInformation model and collects its fields
    """
    states = [
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
    ]

    # Fields that will need to be completed in this form
    user_email = forms.EmailField(label='Email', widget=forms.EmailInput())
    first_name = forms.CharField(label='First Name', max_length=25)
    last_name = forms.CharField(label='Last Name', max_length=25)
    phone_number = forms.IntegerField(label='Phone Number', max_value=9999999999, min_value=1000000000)
    sponsor_company = forms.ModelChoiceField(label='Sponsor', queryset=SponsorCompany.objects.all())
    address = forms.CharField(label='Address', max_length=100)
    license_number = forms.CharField(label='License', max_length=20)
    state = forms.ChoiceField(label='State', choices=states)
    all_companies = forms.ModelMultipleChoiceField(label="All Driver's Companies", queryset=SponsorCompany.objects.all())

    def __init__(self, *args, **kwargs):
        """function __init__ is called to instantiate the user information form

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super(EditUserInformationForm, self).__init__(*args, **kwargs)

        # Validator that makes sure all the fields have been filled in
        for _field_name, field in self.fields.items():
            field.required = True

    class Meta:
        """
        A class that stores the meta information about this form
        """
        model = UserInformation
        fields = ['user_email', 'first_name', 'last_name', 'phone_number', 'sponsor_company', 'address', 'license_number', 'state', 'all_companies']

class EditAdminForm(forms.ModelForm):
    """
    This form creates an instance of a UserInformation model and collects its fields
    """
    states = [
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
    ]

    # Fields that will need to be completed in this form
    user_email = forms.EmailField(label='Email', widget=forms.EmailInput())
    first_name = forms.CharField(label='First Name', max_length=25)
    last_name = forms.CharField(label='Last Name', max_length=25)
    phone_number = forms.IntegerField(label='Phone Number', max_value=9999999999, min_value=1000000000)
    address = forms.CharField(label='Address', max_length=100)
    license_number = forms.CharField(label='License', max_length=20)
    state = forms.ChoiceField(label='State', choices=states)

    def __init__(self, *args, **kwargs):
        """function __init__ is called to instantiate the user information form

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super(EditAdminForm, self).__init__(*args, **kwargs)

        # Validator that makes sure all the fields have been filled in
        for _field_name, field in self.fields.items():
            field.required = True

    class Meta:
        """
        A class that stores the meta information about this form
        """
        model = UserInformation
        fields = ['user_email', 'first_name', 'last_name', 'phone_number', 'address', 'license_number', 'state']

class EditSponsorForm(forms.ModelForm):
    """
    This form creates an instance of a UserInformation model and collects its fields
    """
    states = [
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
    ]

    # Fields that will need to be completed in this form
    user_email = forms.EmailField(label='Email', widget=forms.EmailInput())
    first_name = forms.CharField(label='First Name', max_length=25)
    last_name = forms.CharField(label='Last Name', max_length=25)
    phone_number = forms.IntegerField(label='Phone Number', max_value=9999999999, min_value=1000000000)
    sponsor_company = forms.ModelChoiceField(label='Sponsor', queryset=SponsorCompany.objects.all())
    address = forms.CharField(label='Address', max_length=100)
    license_number = forms.CharField(label='License', max_length=20)
    state = forms.ChoiceField(label='State', choices=states)

    def __init__(self, *args, **kwargs):
        """function __init__ is called to instantiate the user information form

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super(EditSponsorForm, self).__init__(*args, **kwargs)

        # Validator that makes sure all the fields have been filled in
        for _field_name, field in self.fields.items():
            field.required = True

    class Meta:
        """
        A class that stores the meta information about this form
        """
        model = UserInformation
        fields = ['user_email', 'first_name', 'last_name', 'phone_number', 'sponsor_company', 'address', 'license_number', 'state']


class EditUserPointsForm(forms.ModelForm):
    """
    This form creates an instance of a Points Change model and collects its fields
    """

    # Fields that will need to be completed in this form
    change_reason = forms.CharField(label='Reason For Points Change', max_length=100)
    point_change = forms.IntegerField(label='Point Change', max_value=1000000, min_value=-1000000)

    def __init__(self, *args, **kwargs):
        """function __init__ is called to instantiate the user points form

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super(EditUserPointsForm, self).__init__(*args, **kwargs)

        # Validator that makes sure all the fields have been filled in
        for _field_name, field in self.fields.items():
            field.required = True

    class Meta:
        """
        A class that stores the meta information about this form
        """
        model = Points
        fields = ['points']


class SponsorCompanyForm(forms.ModelForm):
    """
    This form creates an instance of a SponsorCompanyForm model and collects its fields
    """

    # Fields that will need to be completed in this form
    company_name = forms.CharField(label="Company Name", max_length=25)
    company_phone_number = forms.IntegerField(label="Phone Number", max_value=9999999999, min_value=1000000000)
    company_street_address = forms.CharField(label="Company Street Address", max_length=32)
    company_city = forms.CharField(label="Company City", max_length=25)
    company_state = forms.CharField(label="Company State", max_length=25)
    company_zipcode = forms.IntegerField(label="Zip Code", max_value=99999, min_value=500)
    company_point_ratio = forms.IntegerField(label="US Cents to Catalog Points Ratio")
    company_about_info = forms.CharField(label="About Sponsor", max_length=1000000)

    def __init__(self, *args, **kwargs):
        """function __init__ is called to instantiate the sponsor company form

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super(SponsorCompanyForm, self).__init__(*args, **kwargs)

        # Validator that makes sure all the fields have been filled in
        for _field_name, field in self.fields.items():
            field.required = True

    class Meta:
        """
        A class that stores the meta information about this form
        """
        model = SponsorCompany
        fields = ['company_name', 'company_phone_number', 'company_street_address', 'company_city', 'company_state', 'company_zipcode', 'company_point_ratio', 'company_about_info']

