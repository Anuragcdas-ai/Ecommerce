from django.views.generic import View, TemplateView, ListView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from .models import Cart, CartItem
from products.models import Product

class CartMixin:
    def get_cart(self, request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            return cart
        else:
            # For anonymous users, we could use session-based cart
            # This is a simplified version
            if not hasattr(self, '_cart'):
                session_cart_id = request.session.get('cart_id')
                if session_cart_id:
                    try:
                        cart = Cart.objects.get(id=session_cart_id, user__isnull=True)
                    except Cart.DoesNotExist:
                        cart = Cart.objects.create(user=None)
                        request.session['cart_id'] = cart.id
                else:
                    cart = Cart.objects.create(user=None)
                    request.session['cart_id'] = cart.id
                self._cart = cart
            return self._cart

class CartDetailView(CartMixin, TemplateView):
    template_name = 'cart/cart_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.get_cart(self.request)
        context['cart'] = cart
        context['cart_items'] = cart.items.all().select_related('product')
        context['total_price'] = cart.get_total_price()
        context['total_items'] = cart.get_total_items()
        return context

@method_decorator(require_POST, name='dispatch')
class CartAddView(CartMixin, View):
    def post(self, request, *args, **kwargs):
        cart = self.get_cart(request)
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        if quantity > product.stock:
            messages.error(request, f'Sorry, only {product.stock} items available.')
            return redirect('products:product_detail', slug=product.slug)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                'price': product.get_display_price()
            }
        )
        
        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                messages.error(request, f'Cannot add more than {product.stock} items.')
                return redirect('cart:cart_detail')
            cart_item.quantity = new_quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} added to cart.')
        
        # Update session if user is not authenticated
        if not request.user.is_authenticated:
            request.session.modified = True
        
        return redirect('cart:cart_detail')

class CartUpdateView(CartMixin, View):
    def post(self, request, *args, **kwargs):
        cart = self.get_cart(request)
        item_id = kwargs.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        if quantity > cart_item.product.stock:
            messages.error(request, f'Sorry, only {cart_item.product.stock} items available.')
        elif quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated.')
        
        return redirect('cart:cart_detail')

class CartRemoveView(CartMixin, View):
    def post(self, request, *args, **kwargs):
        cart = self.get_cart(request)
        item_id = kwargs.get('item_id')
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        product_name = cart_item.product.name
        cart_item.delete()
        
        messages.success(request, f'{product_name} removed from cart.')
        return redirect('cart:cart_detail')