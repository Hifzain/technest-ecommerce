function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function showToast(message, isError = false) {
    const container = document.querySelector('.messages-container') || (function () {
        const div = document.createElement('div');
        div.className = 'messages-container';
        document.body.appendChild(div);
        return div;
    })();

    const toast = document.createElement('div');
    toast.className = 'toast-message' + (isError ? ' error' : '');
    toast.style.borderLeftColor = isError ? '#dc2626' : '';
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(120%)';
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

function updateCartCount(count) {
    document.querySelectorAll('.cart-count:not(.wishlist-count)').forEach(el => {
        el.textContent = count;
        el.classList.add('bump');
        setTimeout(() => el.classList.remove('bump'), 400);
    });
}

function addToCart(productId, buttonEl) {
    const originalText = buttonEl.innerHTML;
    buttonEl.disabled = true;
    buttonEl.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Adding...';

    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'quantity=1',
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message);
                updateCartCount(data.cart_total_items);
                buttonEl.innerHTML = '<i class="fa-solid fa-check"></i> In Cart';
                buttonEl.classList.add('in-cart');
                buttonEl.disabled = false;
            } else if (data.already_in_cart) {
                showToast(data.message, true);
                buttonEl.innerHTML = '<i class="fa-solid fa-check"></i> In Cart';
                buttonEl.classList.add('in-cart');
                buttonEl.disabled = false;
            } else {
                showToast(data.message || 'Something went wrong.', true);
                buttonEl.innerHTML = originalText;
                buttonEl.disabled = false;
            }
        })
        .catch(() => {
            showToast('Network error. Please try again.', true);
            buttonEl.innerHTML = originalText;
            buttonEl.disabled = false;
        });
}
function updateCartItem(itemId, quantity, rowEl) {
    fetch(`/cart/update/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=${quantity}`,
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCartCount(data.cart_total_items);
                if (quantity <= 0) {
                    rowEl.remove();
                } else {
                    rowEl.querySelector('.line-total').textContent = `Rs. ${parseFloat(data.line_total).toFixed(2)}`;
                }
                document.querySelectorAll('.cart-subtotal-value').forEach(el => {
                    el.textContent = `Rs. ${parseFloat(data.cart_subtotal).toFixed(2)}`;
                });
                if (data.cart_total_items === 0) {
                    location.reload();
                }
            } else {
                showToast(data.message, true);
                if (data.max_quantity !== undefined) {
                    const input = rowEl.querySelector('input[type="number"]');
                    input.value = data.max_quantity;
                }
            }
        });
}
function removeCartItem(itemId, rowEl) {
    fetch(`/cart/remove/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCartCount(data.cart_total_items);
                rowEl.remove();
                document.querySelectorAll('.cart-subtotal-value').forEach(el => {
                    el.textContent = `Rs. ${parseFloat(data.cart_subtotal).toFixed(2)}`;
                });
                if (data.cart_total_items === 0) {
                    location.reload();
                }
            }
        });
}
function toggleWishlist(productId, buttonEl) {
    fetch(`/wishlist/toggle/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                buttonEl.classList.toggle('active', data.added);
                showToast(data.added ? 'Added to wishlist' : 'Removed from wishlist');
                document.querySelectorAll('.nav-icons .fa-heart').forEach(icon => {
                    const badge = icon.parentElement.querySelector('.wishlist-count');
                    if (data.wishlist_count > 0) {
                        if (badge) {
                            badge.textContent = data.wishlist_count;
                        } else {
                            const span = document.createElement('span');
                            span.className = 'cart-count wishlist-count';
                            span.textContent = data.wishlist_count;
                            icon.parentElement.appendChild(span);
                        }
                    } else if (badge) {
                        badge.remove();
                    }
                });
            }
        });
}
