from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category, Brand
from .recommendations import get_similar_products


def shop(request):
    products = Product.objects.filter(status=1).select_related('category', 'brand')

    query = request.GET.get('q')
    category_slug = request.GET.get('category')
    brand_slug = request.GET.get('brand')
    sort = request.GET.get('sort')

    if query:
        keywords = [k.strip() for k in query.split() if k.strip()]
        if keywords:
            keyword_filter = Q()
            for kw in keywords:
                keyword_filter |= (
                    Q(name__icontains=kw) |
                    Q(short_description__icontains=kw) |
                    Q(description__icontains=kw) |
                    Q(category__name__icontains=kw) |
                    Q(brand__name__icontains=kw) |
                    Q(specifications__value__icontains=kw)
                )
            products = products.filter(keyword_filter).distinct()

            # Rank by relevance: count how many keywords matched, best matches first
            from django.db.models import Case, When, IntegerField, Value
            relevance_cases = []
            for kw in keywords:
                relevance_cases.append(
                    When(name__icontains=kw, then=Value(3))
                )
                relevance_cases.append(
                    When(short_description__icontains=kw, then=Value(1))
                )
            if relevance_cases:
                products = products.annotate(
                    relevance=Case(*relevance_cases, default=Value(0), output_field=IntegerField())
                )
                if not sort:
                    products = products.order_by('-relevance', '-date_created')

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if brand_slug:
        products = products.filter(brand__slug=brand_slug)

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'best_selling':
        products = products.order_by('-sales_count')
    else:
        products = products.order_by('-date_created')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.filter(is_active=True),
        'brands': Brand.objects.filter(is_active=True),
        'query': query or '',
        'selected_category': category_slug or '',
        'selected_brand': brand_slug or '',
        'selected_sort': sort or '',
    }
    return render(request, 'products/shop.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, status=1).order_by('-date_created')

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'products/category_detail.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category', 'brand').prefetch_related('images', 'specifications', 'reviews__user'),
        slug=slug, status=1
    )

    Product.objects.filter(pk=product.pk).update(views_count=product.views_count + 1)

    similar_products = get_similar_products(product, top_n=4)

    user_review = None
    user_can_review = False
    if request.user.is_authenticated:
        user_review = product.reviews.filter(user=request.user).first()
        from apps.orders.models import OrderItem
        user_can_review = OrderItem.objects.filter(order__user=request.user, product=product).exists()

    context = {
        'product': product,
        'similar_products': similar_products,
        'reviews': product.reviews.filter(is_approved=True),
        'user_review': user_review,
        'user_can_review': user_can_review,
    }
    return render(request, 'products/product_detail.html', context)