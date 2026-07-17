from .models import Cart


def get_or_create_cart(request):
    """
    Returns the current cart:
    - Logged in users: cart tied to their account
    - Guests: cart tied to their session
    Also merges a guest cart into the user's cart on login (called from accounts views).
    """
    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)

    return cart


def merge_guest_cart_into_user(request, user):
    """Call this right after login so items added as a guest aren't lost."""
    session_key = request.session.session_key
    if not session_key:
        return

    try:
        guest_cart = Cart.objects.get(session_key=session_key, user=None)
    except Cart.DoesNotExist:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)

    for item in guest_cart.items.all():
        existing = user_cart.items.filter(product=item.product).first()
        if existing:
            existing.quantity += item.quantity
            existing.save()
        else:
            item.cart = user_cart
            item.save()

    guest_cart.delete()