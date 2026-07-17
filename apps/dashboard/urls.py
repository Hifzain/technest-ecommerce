from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),

    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/toggle-status/', views.product_toggle_status, name='product_toggle_status'),
    path('products/<int:pk>/toggle-featured/', views.product_toggle_featured, name='product_toggle_featured'),

    path('orders/', views.order_list, name='order_list'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('orders/<str:order_number>/update-status/', views.order_update_status, name='order_update_status'),

    path('customers/', views.customer_list, name='customer_list'),

    path('reports/sales/', views.sales_report, name='sales_report'),
]