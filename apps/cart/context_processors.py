def cart_context(request):
    from .utils import get_or_create_cart
    try:
        cart = get_or_create_cart(request)
        ids = set(cart.items.values_list('product_id', flat=True))
        total_items = cart.total_items
    except Exception:
        ids = set()
        total_items = 0
    return {'cart_product_ids': ids, 'cart_total_items': total_items}