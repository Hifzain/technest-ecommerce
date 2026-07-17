from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.products.models import Product
from apps.orders.models import OrderItem
from .models import Review


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    has_purchased = OrderItem.objects.filter(
        order__user=request.user, product=product
    ).exists()

    if request.method == "POST":
        rating = int(request.POST.get("rating", 5))
        title = request.POST.get("title", "")
        comment = request.POST.get("comment", "")

        review, created = Review.objects.update_or_create(
            product=product, user=request.user,
            defaults={
                "rating": rating,
                "title": title,
                "comment": comment,
                "is_verified_purchase": has_purchased,
            }
        )
        messages.success(request, "Your review has been submitted!" if created else "Your review has been updated!")
        return redirect("products:product_detail", slug=product.slug)

    return redirect("products:product_detail", slug=product.slug)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    product_slug = review.product.slug
    review.delete()
    messages.info(request, "Your review has been deleted.")
    return redirect("products:product_detail", slug=product_slug)
