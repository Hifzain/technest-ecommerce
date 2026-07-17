def wishlist_context(request):
    if request.user.is_authenticated:
        ids = set(request.user.wishlist_items.values_list('product_id', flat=True))
        return {'user_wishlist_ids': ids, 'wishlist_count': len(ids)}
    return {'user_wishlist_ids': set(), 'wishlist_count': 0}