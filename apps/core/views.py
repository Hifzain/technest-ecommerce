from django.shortcuts import render, redirect
from django.contrib import messages
from apps.products.models import Product, Category
from django.views.decorators.cache import cache_page
from .models import ContactMessage, FAQ, HeroSlide


# @cache_page(60 * 5)
# def home(request):
#     context = {
#         'hero_slides': HeroSlide.objects.filter(is_active=True),
#         'categories': Category.objects.filter(is_active=True)[:8],
#         'best_sellers': Product.objects.filter(status=1).order_by('-sales_count')[:8],
#         'featured_products': Product.objects.filter(status=1, is_featured=True)[:8],
#         'on_sale_products': [p for p in Product.objects.filter(status=1) if p.is_on_sale][:8],
#     }
#     return render(request, 'core/home.html', context)
from django.http import HttpResponse

def home(request):
    return HttpResponse("Home is working")

def about(request):
    return render(request, 'core/about.html')


def contact(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
        )
        messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
        return redirect('core:contact')

    return render(request, 'core/contact.html')


def faq(request):
    faqs = FAQ.objects.filter(is_active=True)
    categories = FAQ.CATEGORY_CHOICES

    grouped = {}
    for cat_key, cat_label in categories:
        items = faqs.filter(category=cat_key)
        if items.exists():
            grouped[cat_label] = items

    return render(request, 'core/faq.html', {'grouped_faqs': grouped})