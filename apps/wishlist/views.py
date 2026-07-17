from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.products.models import Product
from .models import Wishlist


@login_required
def wishlist_detail(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist/wishlist_detail.html', {'items': items})


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    existing = Wishlist.objects.filter(user=request.user, product=product).first()

    if existing:
        existing.delete()
        added = False
    else:
        Wishlist.objects.create(user=request.user, product=product)
        added = True

    return JsonResponse({
        'success': True,
        'added': added,
        'wishlist_count': Wishlist.objects.filter(user=request.user).count(),
    })