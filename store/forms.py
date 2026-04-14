from django import forms
from .models import Rating

class formRating(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['subject', 'review', 'rating']