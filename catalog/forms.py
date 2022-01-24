"""
This module contains custom forms used to collect the information needed to create a model.
"""
from django import forms
from .models import ItemReview

class ItemReviewForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    review = forms.CharField(widget=forms.Textarea(attrs={"rows":10, "cols":50}))