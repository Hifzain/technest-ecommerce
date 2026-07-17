from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from apps.cart.utils import get_or_create_cart
from apps.accounts.models import Address
from .models import Order, OrderItem

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout(request):
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect("products:shop")

    addresses = request.user.addresses.all()

    if request.method == "POST":
        address_id = request.POST.get("address_id")
        payment_method = request.POST.get("payment_method", "0")
        notes = request.POST.get("notes", "")

        address = get_object_or_404(
            Address,
            pk=address_id,
            user=request.user
        )

        # Check stock availability before placing order
        for item in cart.items.all():
            if item.quantity > item.product.stock_quantity:
                messages.error(
                    request,
                    f"Sorry, only {item.product.stock_quantity} of {item.product.name} left in stock."
                )
                return redirect("cart:cart_detail")

        # Create order inside a database transaction
        with transaction.atomic():
            subtotal = cart.subtotal
            shipping_cost = 0 if subtotal >= 5000 else 250  # Free shipping over Rs. 5000

            order = Order.objects.create(
                user=request.user,
                address=address,
                shipping_full_name=address.full_name,
                shipping_phone=address.phone_number,
                shipping_address_line=address.address_line,
                shipping_city=address.city,
                shipping_postal_code=address.postal_code,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                total=subtotal + shipping_cost,
                payment_method=int(payment_method),
                notes=notes,
            )

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.current_price,
                    quantity=item.quantity,
                )

                # Update product stock
                item.product.stock_quantity = max(
                    0,
                    item.product.stock_quantity - item.quantity
                )
                item.product.sales_count += item.quantity
                item.product.save()

            # Clear cart after successful order
            cart.items.all().delete()

        # Redirect to Stripe payment if card is selected
        if int(payment_method) == 1:
            return redirect(
                "orders:create_stripe_session",
                order_number=order.order_number
            )

        messages.success(
            request,
            f"Order {order.order_number} placed successfully!"
        )
        return redirect(
            "orders:order_confirmation",
            order_number=order.order_number
        )

    context = {
        "cart": cart,
        "addresses": addresses,
    }

    return render(request, "orders/checkout.html", context)


@login_required
def order_confirmation(request, order_number):
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )
    return render(
        request,
        "orders/order_confirmation.html",
        {"order": order}
    )


@login_required
def order_history(request):
    orders = request.user.orders.all()
    return render(
        request,
        "orders/order_history.html",
        {"orders": orders}
    )


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )
    return render(
        request,
        "orders/order_detail.html",
        {"order": order}
    )
@login_required
def create_stripe_session(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    line_items = []
    for item in order.items.all():
        line_items.append({
            'price_data': {
                'currency': 'pkr',
                'product_data': {'name': item.product_name},
                'unit_amount': int(item.price * 100),  # Stripe uses smallest currency unit
            },
            'quantity': item.quantity,
        })

    if order.shipping_cost > 0:
        line_items.append({
            'price_data': {
                'currency': 'pkr',
                'product_data': {'name': 'Shipping'},
                'unit_amount': int(order.shipping_cost * 100),
            },
            'quantity': 1,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(
            reverse('orders:stripe_success', args=[order.order_number])
        ) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(
            reverse('orders:stripe_cancel', args=[order.order_number])
        ),
        metadata={'order_number': order.order_number},
    )

    order.stripe_session_id = session.id
    order.save()

    return redirect(session.url, permanent=False)


@login_required
def stripe_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    session_id = request.GET.get('session_id')

    if session_id:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            order.payment_status = 1  # Paid
            order.status = 1  # Processing
            order.save()
            messages.success(request, f"Payment successful! Order {order.order_number} confirmed.")
        else:
            messages.warning(request, "Payment not confirmed yet. We'll update your order shortly.")

    return redirect('orders:order_confirmation', order_number=order.order_number)


@login_required
def stripe_cancel(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    messages.warning(request, "Payment was cancelled. You can try again or choose Cash on Delivery.")
    return redirect('orders:order_detail', order_number=order.order_number)