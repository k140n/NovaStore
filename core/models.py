from django.db import models
from django.utils.html import mark_safe


class BannerQuerySet(models.QuerySet):
    def active(self):
        """Return only active banners ordered by display order then newest."""
        return self.filter(is_active=True).order_by("order", "-created_at")


class Banner(models.Model):
    """
    Dynamic banner model for storefront promotions and hero carousels.
    Administrators have full CRUD control over images, links, copy, order, and visibility.
    """
    title = models.CharField(
        max_length=200,
        help_text="Primary headline (e.g. 'MacBook Pro. Mind-blowing. Head-turning.')",
    )
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        help_text="Secondary tagline or offer description",
    )
    description = models.TextField(
        blank=True,
        help_text="Optional extended copy for detailed promotional banners",
    )
    badge_text = models.CharField(
        max_length=50,
        blank=True,
        help_text="Highlight badge (e.g. 'New Release', 'Flagship', 'Special Offer')",
    )
    image = models.ImageField(
        upload_to="banners/%Y/%m/",
        help_text="High-resolution banner graphic (recommended 1920x800 or 1600x600)",
    )
    button_text = models.CharField(
        max_length=60,
        default="Learn More",
        help_text="Call to action button label",
    )
    button_link = models.CharField(
        max_length=255,
        default="/catalog/",
        help_text="Target URL or relative path (e.g. '/catalog/laptops/')",
    )
    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Display order sequence (lower numbers display first)",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Enable or disable banner display on public site",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BannerQuerySet.as_manager()

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        indexes = [
            models.Index(fields=["is_active", "order"]),
        ]

    def __str__(self):
        return self.title

    def image_preview_thumb(self):
        """Thumbnail display for admin list views."""
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" style="width: 80px; height: 45px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />'
            )
        return "No Image"
    image_preview_thumb.short_description = "Preview"

    def image_preview_large(self):
        """Enlarged image preview for change view forms."""
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" style="max-width: 480px; height: auto; border-radius: 8px; border: 1px solid #ddd; margin-top: 8px;" />'
            )
        return "No Image Uploaded"
    image_preview_large.short_description = "Image Preview"
