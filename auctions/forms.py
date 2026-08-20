from django import forms
from .models import Auction

class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'description', 'starting_bid', 'image', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auction Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description...'}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Starting Bid ($)'}),
            'image': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Image URL (Optional)'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }