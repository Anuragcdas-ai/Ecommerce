from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('complete/', views.OrderCompleteView.as_view(), name='order_complete'),
    path('history/', views.OrderHistoryView.as_view(), name='order_history'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    
    # Shipping addresses
    path('addresses/', views.ShippingAddressListView.as_view(), name='shipping_address_list'),
    path('addresses/add/', views.ShippingAddressCreateView.as_view(), name='shipping_address_add'),
    path('addresses/<int:pk>/edit/', views.ShippingAddressUpdateView.as_view(), name='shipping_address_edit'),
]