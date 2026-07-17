from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
import json

from .permissions import staff_required
from .utils import get_dashboard_stats, get_sales_trend_data, get_top_products_data, get_order_status_breakdown
from apps.products.models import Product, Category, Brand, Promotion
from apps.orders.models import Order


@login_required
@staff_required
def dashboard_home(request):
    context = {
        'stats': get_dashboard_stats(),
        'sales_trend': json.dumps(get_sales_trend_data()),
        'top_products': json.dumps(get_top_products_data()),
        'order_status': json.dumps(get_order_status_breakdown()),
        'recent_orders': Order.objects.all()[:5],
    }
    return render(request, 'dashboard/home.html', context)


# ---------- Products ----------

@login_required
@staff_required
def product_list(request):
    products = Product.objects.select_related('category', 'brand').all()

    query = request.GET.get('q')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query))

    paginator = Paginator(products, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/products/list.html', {'page_obj': page_obj, 'query': query or ''})


@login_required
@staff_required
def product_toggle_status(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.status = 2 if product.status == 1 else 1
    product.save()
    messages.success(request, f"{product.name} status updated.")
    return redirect('dashboard:product_list')


@login_required
@staff_required
def product_toggle_featured(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_featured = not product.is_featured
    product.save()
    messages.success(request, f"{product.name} featured status updated.")
    return redirect('dashboard:product_list')


# ---------- Orders ----------

@login_required
@staff_required
def order_list(request):
    orders = Order.objects.select_related('user').all()

    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    paginator = Paginator(orders, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/orders/list.html', {
        'page_obj': page_obj,
        'status_choices': Order.STATUS_CHOICES,
        'selected_status': status_filter or '',
    })


@login_required
@staff_required
def order_update_status(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = int(new_status)
        if order.payment_method == 0 and order.status == 3:  # COD delivered = paid
            order.payment_status = 1
        order.save()
        messages.success(request, f"Order {order.order_number} updated.")
    return redirect('dashboard:order_list')


@login_required
@staff_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'dashboard/orders/detail.html', {'order': order})


# ---------- Customers ----------

@login_required
@staff_required
def customer_list(request):
    from apps.accounts.models import User
    customers = User.objects.filter(is_staff=False).order_by('-date_joined')

    paginator = Paginator(customers, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/customers/list.html', {'page_obj': page_obj})


# ---------- Reports ----------

@login_required
@staff_required
def sales_report(request):
    context = {
        'sales_trend': json.dumps(get_sales_trend_data(days=30)),
        'top_products': json.dumps(get_top_products_data(limit=10)),
        'order_status': json.dumps(get_order_status_breakdown()),
    }
    return render(request, 'dashboard/reports/sales_report.html', context)