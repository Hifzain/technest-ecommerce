from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.subject} - {self.name}"


class FAQ(models.Model):
    CATEGORY_CHOICES = (
        ('general', 'General'),
        ('orders', 'Orders & Shipping'),
        ('payment', 'Payment'),
        ('returns', 'Returns & Warranty'),
        ('account', 'Account'),
    )

    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['category', 'order', 'question']

    def __str__(self):
        return self.question

class HeroSlide(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='hero_slides/')
    badge_text = models.CharField(max_length=100, blank=True, help_text="e.g. 'Free shipping on orders over Rs. 5,000'")
    button_text = models.CharField(max_length=50, default="Shop Now")
    button_link = models.CharField(max_length=255, default="/shop/")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-date_created']

    def __str__(self):
        return self.title