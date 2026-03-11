from django.views.generic import CreateView, UpdateView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django import forms
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .models import Profile
from orders.models import Order

# Extended User Creation Form with Profile fields
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=20, required=False)
    newsletter = forms.BooleanField(required=False, initial=False)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create profile with additional fields
            profile = user.profile
            profile.phone = self.cleaned_data.get('phone', '')
            profile.newsletter_subscription = self.cleaned_data.get('newsletter', False)
            profile.save()
        
        return user

# User Edit Form with Profile fields
class UserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=20, required=False)
    newsletter = forms.BooleanField(required=False)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            try:
                self.fields['phone'].initial = self.instance.profile.phone
                self.fields['newsletter'].initial = self.instance.profile.newsletter_subscription
            except Profile.DoesNotExist:
                pass
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Update profile
            profile = user.profile
            profile.phone = self.cleaned_data.get('phone', '')
            profile.newsletter_subscription = self.cleaned_data.get('newsletter', False)
            profile.save()
        return user

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        messages.success(self.request, 'Account created successfully! You can now log in.')
        return super().form_valid(form)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_orders'] = Order.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:5]
        context['profile'] = self.request.user.profile
        return context

class ProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = UserEditForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class ProfileImageUploadView(LoginRequiredMixin, FormView):
    template_name = 'accounts/profile_image_upload.html'
    success_url = reverse_lazy('accounts:profile')
    
    class UploadForm(forms.Form):
        profile_image = forms.ImageField(required=True)
    
    def get_form_class(self):
        return self.UploadForm
    
    def form_valid(self, form):
        profile = self.request.user.profile
        profile.profile_image = form.cleaned_data['profile_image']
        profile.save()
        messages.success(self.request, 'Profile image updated successfully!')
        return super().form_valid(form)

class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)