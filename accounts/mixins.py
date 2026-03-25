from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages

class MerchantRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verify that the current user is a verified merchant."""
    
    def test_func(self):
        return self.request.user.profile.is_merchant()
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        
        if self.request.user.profile.user_type == 'merchant' and not self.request.user.profile.is_verified_merchant:
            messages.warning(self.request, 'Your merchant account is pending verification.')
            return redirect('accounts:merchant_pending')
        else:
            messages.warning(self.request, 'You need a merchant account to access this page.')
            return redirect('accounts:become_merchant')

class ProductOwnerMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Verify that the current user owns the product."""
    
    def test_func(self):
        product = self.get_object()
        return product.merchant == self.request.user or self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to modify this product.')
        return redirect('products:product_list')