from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
from .models import Order, OrderItem, ShippingAddress
from cart.models import Cart
from cart.views import CartMixin
from decimal import Decimal

class CheckoutView(LoginRequiredMixin, CartMixin, TemplateView):
    template_name = 'orders/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.get_cart(self.request)
        
        if cart.get_total_items() == 0:
            messages.warning(self.request, 'Your cart is empty.')
            return context
        
        context['cart'] = cart
        context['cart_items'] = cart.items.all()
        context['total_price'] = cart.get_total_price()
        context['shipping_addresses'] = ShippingAddress.objects.filter(user=self.request.user)
        context['default_address'] = ShippingAddress.objects.filter(
            user=self.request.user, is_default=True
        ).first()
        
        return context

class OrderCreateView(LoginRequiredMixin, CartMixin, CreateView):
    model = Order
    fields = [
        'first_name', 'last_name', 'email', 'phone',
        'address', 'address2', 'city', 'state',
        'postal_code', 'country', 'payment_method', 'notes'
    ]
    template_name = 'orders/order_create.html'
    success_url = reverse_lazy('orders:order_complete')

    def dispatch(self, request, *args, **kwargs):
        self.cart = self.get_cart(request)

        if self.cart.get_total_items() == 0:
            messages.warning(request, 'Your cart is empty.')
            return redirect('products:product_list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        subtotal = self.cart.get_total_price()
        shipping_cost = Decimal('0.00')
        tax = subtotal * Decimal('0.10')
        total = subtotal + shipping_cost + tax

        context['cart'] = self.cart
        context['cart_items'] = self.cart.items.all()
        context['subtotal'] = subtotal
        context['shipping_cost'] = shipping_cost
        context['tax'] = tax
        context['total'] = total

        return context

    @transaction.atomic
    def form_valid(self, form):

        subtotal = self.cart.get_total_price()
        shipping_cost = Decimal('0.00')
        tax = subtotal * Decimal('0.10')
        total = subtotal + shipping_cost + tax

        form.instance.user = self.request.user
        form.instance.subtotal = subtotal
        form.instance.shipping_cost = shipping_cost
        form.instance.tax = tax
        form.instance.total = total

        response = super().form_valid(form)

        for cart_item in self.cart.items.all():

            OrderItem.objects.create(
                order=self.object,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.price,
                quantity=cart_item.quantity
            )

            # update stock
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()

        self.cart.clear()

        self.request.session['order_id'] = self.object.id

        messages.success(self.request, "Your order has been placed successfully!")

        return response
        
    

class OrderCompleteView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/order_complete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.request.session.get('order_id')
        
        if order_id:
            order = get_object_or_404(Order, id=order_id, user=self.request.user)
            context['order'] = order
            del self.request.session['order_id']
        else:
            context['order'] = None
        
        return context

class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class ShippingAddressListView(LoginRequiredMixin, ListView):
    model = ShippingAddress
    template_name = 'orders/shipping_address_list.html'
    context_object_name = 'addresses'
    
    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

class ShippingAddressCreateView(LoginRequiredMixin, CreateView):
    model = ShippingAddress
    fields = ['first_name', 'last_name', 'phone', 'address', 'address2', 
              'city', 'state', 'postal_code', 'country', 'is_default']
    template_name = 'orders/shipping_address_form.html'
    success_url = reverse_lazy('orders:shipping_address_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # If this is set as default, remove default from others
        if form.instance.is_default:
            ShippingAddress.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
        
        return super().form_valid(form)

class ShippingAddressUpdateView(LoginRequiredMixin, UpdateView):
    model = ShippingAddress
    fields = ['first_name', 'last_name', 'phone', 'address', 'address2', 
              'city', 'state', 'postal_code', 'country', 'is_default']
    template_name = 'orders/shipping_address_form.html'
    success_url = reverse_lazy('orders:shipping_address_list')
    
    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        # If this is set as default, remove default from others
        if form.instance.is_default:
            ShippingAddress.objects.filter(user=self.request.user, is_default=True).exclude(
                id=form.instance.id
            ).update(is_default=False)
        
        return super().form_valid(form)