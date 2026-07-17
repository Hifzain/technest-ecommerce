from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from apps.orders.models import Order, OrderItem
from apps.products.models import Product


def get_dashboard_stats():
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)

    orders_qs = Order.objects.exclude(status=4)  # exclude cancelled

    total_revenue = orders_qs.aggregate(total=Sum('total'))['total'] or 0
    total_orders = orders_qs.count()
    total_products = Product.objects.filter(status=1).count()
    pending_orders = Order.objects.filter(status=0).count()
    low_stock_products = Product.objects.filter(status=1, stock_quantity__lte=5).count()

    return {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_products': total_products,
        'pending_orders': pending_orders,
        'low_stock_products': low_stock_products,
    }


def get_sales_trend_data(days=14):
    """Daily revenue for the last N days, formatted for Chart.js."""
    start_date = timezone.now().date() - timedelta(days=days - 1)

    daily_sales = (
        Order.objects.exclude(status=4)
        .filter(date_created__date__gte=start_date)
        .annotate(day=TruncDate('date_created'))
        .values('day')
        .annotate(revenue=Sum('total'))
        .order_by('day')
    )

    sales_by_day = {entry['day']: float(entry['revenue']) for entry in daily_sales}

    labels = []
    data = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        labels.append(day.strftime('%b %d'))
        data.append(sales_by_day.get(day, 0))

    return {'labels': labels, 'data': data}


def get_top_products_data(limit=5):
    products = Product.objects.filter(status=1).order_by('-sales_count')[:limit]
    return {
        'labels': [p.name for p in products],
        'data': [p.sales_count for p in products],
    }


def get_order_status_breakdown():
    breakdown = Order.objects.values('status').annotate(count=Count('id')).order_by('status')
    status_map = dict(Order.STATUS_CHOICES)
    return {
        'labels': [status_map.get(item['status'], 'Unknown') for item in breakdown],
        'data': [item['count'] for item in breakdown],
    }