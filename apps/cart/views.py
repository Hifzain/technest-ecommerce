from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.products.models import Product
from .utils import get_or_create_cart
from .models import CartItem


def cart_detail(request):
    cart = get_or_create_cart(request)
    return render(request, "cart/cart_detail.html", {"cart": cart})

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, status=1)
    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))

    existing_item = CartItem.objects.filter(cart=cart, product=product).first()

    if existing_item:
        return JsonResponse({
            'success': False,
            'already_in_cart': True,
            'message': f"{product.name} is already in your cart.",
            'cart_total_items': cart.total_items,
        })

    if quantity > product.stock_quantity:
        return JsonResponse({
            'success': False,
            'message': f"Only {product.stock_quantity} left in stock.",
            'cart_total_items': cart.total_items,
        })

    CartItem.objects.create(cart=cart, product=product, quantity=quantity)

    return JsonResponse({
        'success': True,
        'message': f"{product.name} added to cart",
        'cart_total_items': cart.total_items,
    })


@require_POST
def update_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        item.delete()
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
            'line_total': '0',
        })

    if quantity > item.product.stock_quantity:
        return JsonResponse({
            'success': False,
            'message': f"Only {item.product.stock_quantity} available for {item.product.name}.",
            'max_quantity': item.product.stock_quantity,
            'cart_total_items': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
        })

    item.quantity = quantity
    item.save()

    return JsonResponse({
        'success': True,
        'cart_total_items': cart.total_items,
        'cart_subtotal': str(cart.subtotal),
        'line_total': str(item.line_total),
    })

@require_POST
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()

    return JsonResponse({
        "success": True,
        "cart_total_items": cart.total_items,
        "cart_subtotal": str(cart.subtotal),
    })
