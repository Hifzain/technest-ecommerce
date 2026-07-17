from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('history/', views.order_history, name='order_history'),
    path('stripe/create-session/<str:order_number>/', views.create_stripe_session, name='create_stripe_session'),
    path('stripe/success/<str:order_number>/', views.stripe_success, name='stripe_success'),
    path('stripe/cancel/<str:order_number>/', views.stripe_cancel, name='stripe_cancel'),
    path('<str:order_number>/', views.order_detail, name='order_detail'),
]