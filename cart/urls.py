from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartDetailView.as_view(), name='cart_detail'),
    path('add/', views.CartAddView.as_view(), name='cart_add'),
    path('update/<int:item_id>/', views.CartUpdateView.as_view(), name='cart_update'),
    path('remove/<int:item_id>/', views.CartRemoveView.as_view(), name='cart_remove'),
]