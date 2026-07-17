from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, Specification, Promotion


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'date_created')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'discount_price', 'stock_quantity', 'status', 'is_featured', 'sales_count')
    list_filter = ('category', 'brand', 'status', 'is_featured')
    search_fields = ('name', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, SpecificationInline]


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'scope', 'discount_type', 'discount_value', 'start_date', 'end_date', 'is_active', 'is_live')
    list_filter = ('scope', 'discount_type', 'is_active')
    search_fields = ('name',)
    filter_horizontal = ('products',)

    def is_live(self, obj):
        return obj.is_live
    is_live.boolean = True