from django import forms
from .models import Product

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'