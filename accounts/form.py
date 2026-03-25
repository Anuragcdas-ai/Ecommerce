# forms.py
from django import forms

class MerchantRegisterForm(forms.Form):
    # User fields
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    # Essential merchant fields
    company_name = forms.CharField(max_length=200)
    business_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    tax_id = forms.CharField(max_length=50)
    business_phone = forms.CharField(max_length=20)
    business_email = forms.EmailField()