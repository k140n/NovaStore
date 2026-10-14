from django.contrib import admin
from .models import Category, Product, ProductSpecification


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 3
    fields = ["name", "value", "order"]
    classes = ["collapse"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "image_preview_thumb",
        "name",
        "slug",
        "product_count",
        "order",
        "is_active",
        "created_at",
    ]
    list_display_links = ["name"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["image_preview_large", "product_count", "created_at", "updated_at"]
    ordering = ["order", "name"]

    fieldsets = (
        ("Category Overview", {
            "fields": ("name", "slug", "description"),
            "description": "Category naming and descriptive metadata",
        }),
        ("Media & Visuals", {
            "fields": ("image", "image_preview_large", "icon_name"),
            "description": "Category card thumbnail and iconography",
        }),
        ("Ordering & Publication", {
            "fields": ("order", "is_active"),
            "description": "Positioning in category strips and live visibility",
        }),
        ("Metadata", {
            "fields": ("product_count", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "image_preview_thumb",
        "name",
        "category",
        "price",
        "original_price",
        "stock",
        "is_featured",
        "is_active",
        "updated_at",
    ]
    list_display_links = ["name"]
    list_editable = ["price", "is_featured", "is_active", "stock"]
    list_filter = ["category", "is_active", "is_featured", "created_at"]
    search_fields = ["name", "tagline", "description", "category__name"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["image_preview_large", "created_at", "updated_at"]
    inlines = [ProductSpecificationInline]
    ordering = ["-is_featured", "-created_at"]

    fieldsets = (
        ("Product Identity", {
            "fields": ("name", "slug", "category", "tagline", "description"),
            "description": "Core descriptive details and category mapping",
        }),
        ("Pricing & Inventory", {
            "fields": ("price", "original_price", "stock"),
            "description": "Storefront price, optional MRP discount reference, and stock quantity",
        }),
        ("Product Imagery", {
            "fields": ("image", "image_preview_large"),
            "description": "High quality product photography",
        }),
        ("Storefront Visibility & Placement", {
            "fields": ("is_active", "is_featured"),
            "description": "Control if the product is live in listings and highlighted as featured",
        }),
        ("System Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
