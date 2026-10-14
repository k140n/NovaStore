from django.contrib import admin
from .models import Banner

# Admin site customizations
admin.site.site_header = "NovaStore Administration"
admin.site.site_title = "NovaStore Admin Portal"
admin.site.index_title = "Electronics Store Management"


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = [
        "image_preview_thumb",
        "title",
        "badge_text",
        "button_text",
        "button_link",
        "order",
        "is_active",
        "created_at",
    ]
    list_display_links = ["title"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["title", "subtitle", "description", "badge_text", "button_link"]
    readonly_fields = ["image_preview_large", "created_at", "updated_at"]
    ordering = ["order", "-created_at"]

    fieldsets = (
        ("Banner Content", {
            "fields": ("title", "subtitle", "description", "badge_text"),
            "description": "Copy and marketing headlines shown on the banner",
        }),
        ("Media & Imagery", {
            "fields": ("image", "image_preview_large"),
            "description": "Upload high-resolution graphics for storefront display",
        }),
        ("Action Button & Destination", {
            "fields": ("button_text", "button_link"),
            "description": "Call-to-action button text and redirection URL",
        }),
        ("Display Controls & Status", {
            "fields": ("order", "is_active"),
            "description": "Control display order (lower = first) and live publication status",
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
