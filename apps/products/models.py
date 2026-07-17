from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome class, e.g. fa-solid fa-microchip")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = (
        (0, 'Draft'),
        (1, 'Active'),
        (2, 'Out of Stock'),
        (3, 'Discontinued'),
    )

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)

    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    stock_quantity = models.PositiveIntegerField(default=0)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)

    is_featured = models.BooleanField(default=False)
    sales_count = models.PositiveIntegerField(default=0, help_text="Auto-incremented when an order is placed")
    views_count = models.PositiveIntegerField(default=0, help_text="Auto-incremented on product page view")

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_created']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.sku}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    @property
    def active_promotion(self):
        """Returns the best currently-live promotion applicable to this product, if any."""
        now = timezone.now()
        candidates = Promotion.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now,
        ).order_by('-priority')

        for promo in candidates:
            if promo.applies_to(self):
                return promo
        return None

    @property
    def current_price(self):
        """
        Priority: manual discount_price (set directly on product) > active promotion > regular price.
        """
        if self.discount_price:
            return self.discount_price

        promo = self.active_promotion
        if promo:
            return promo.calculate_price(self.price)

        return self.price

    @property
    def discount_percentage(self):
        if self.current_price < self.price and self.price > 0:
            return round(((self.price - self.current_price) / self.price) * 100)
        return 0

    @property
    def is_on_sale(self):
        return self.current_price < self.price

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    def __str__(self):
        return self.name
    
    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if not reviews.exists():
            return 0
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=150, blank=True)
    is_primary = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'date_created']

    def __str__(self):
        return f"{self.product.name} - Image"


class Specification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    key = models.CharField(max_length=100, help_text="e.g. Processor, RAM, Storage")
    value = models.CharField(max_length=250, help_text="e.g. Intel Core i7-13700K")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.key}: {self.value}"


class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        (0, 'Percentage (%)'),
        (1, 'Fixed Amount'),
    )
    SCOPE_CHOICES = (
        (0, 'Entire Store'),
        (1, 'Specific Category'),
        (2, 'Specific Products'),
    )

    name = models.CharField(max_length=150, help_text="e.g. 'Eid Sale', 'Flash Friday', 'GPU Clearance'")
    banner_text = models.CharField(max_length=200, blank=True, help_text="Shown on site, e.g. 'Up to 30% off GPUs'")

    scope = models.PositiveSmallIntegerField(choices=SCOPE_CHOICES, default=0)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True,
        related_name='promotions', help_text="Required only if scope = Specific Category"
    )
    products = models.ManyToManyField(
        Product, blank=True, related_name='promotions',
        help_text="Required only if scope = Specific Products"
    )

    discount_type = models.PositiveSmallIntegerField(choices=DISCOUNT_TYPE_CHOICES, default=0)
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Enter 20 for 20% if percentage, or e.g. 500 for Rs.500 off if fixed"
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(
        default=0, help_text="If a product qualifies for multiple promotions, higher priority wins"
    )

    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority', '-date_created']

    def __str__(self):
        return self.name

    @property
    def is_live(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def applies_to(self, product):
        if self.scope == 0:
            return True
        if self.scope == 1:
            return product.category_id == self.category_id
        if self.scope == 2:
            return self.products.filter(pk=product.pk).exists()
        return False

    def calculate_price(self, base_price):
        if self.discount_type == 0:  # percentage
            discount_amount = (base_price * self.discount_value) / 100
        else:  # fixed
            discount_amount = self.discount_value
        final_price = base_price - discount_amount
        return max(final_price, 0)