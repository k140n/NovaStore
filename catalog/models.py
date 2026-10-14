from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.html import mark_safe


class CategoryQuerySet(models.QuerySet):
    def active(self):
        """Return only active categories ordered by display order then name."""
        return self.filter(is_active=True).order_by("order", "name")


class Category(models.Model):
    """
    Electronics category model (e.g. Laptops, Smartphones, Tablets, Audio, Accessories).
    """
    name = models.CharField(max_length=100, unique=True, help_text="Category name (e.g. 'Laptops', 'Audio')")
    slug = models.SlugField(max_length=120, unique=True, db_index=True, help_text="URL-friendly slug (e.g. 'laptops')")
    description = models.TextField(blank=True, help_text="Category overview for category landing pages")
    image = models.ImageField(upload_to="categories/%Y/%m/", blank=True, null=True, help_text="Category thumbnail/header graphic")
    icon_name = models.CharField(max_length=50, blank=True, help_text="Optional icon identifier or SVG name")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Display category on public website")
    order = models.PositiveIntegerField(default=0, db_index=True, help_text="Display order (lower = first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CategoryQuerySet.as_manager()

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:category_detail", kwargs={"slug": self.slug})

    def product_count(self):
        """Return count of active products belonging to this category."""
        return self.products.filter(is_active=True).count()
    product_count.short_description = "Active Products"

    def image_preview_thumb(self):
        """Thumbnail display for admin list view."""
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd;" />'
            )
        return "No Image"
    image_preview_thumb.short_description = "Image"

    def image_preview_large(self):
        """Enlarged image preview for change view forms."""
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" style="max-width: 320px; height: auto; border-radius: 8px; border: 1px solid #ddd; margin-top: 8px;" />'
            )
        return "No Image Uploaded"
    image_preview_large.short_description = "Image Preview"


class ProductQuerySet(models.QuerySet):
    def active(self):
        """Return only active products."""
        return self.filter(is_active=True)

    def featured(self):
        """Return active products marked as featured for homepage showcase."""
        return self.filter(is_active=True, is_featured=True)


class Product(models.Model):
    """
    Electronics product model with pricing, status, specs, and Apple-store style presentation fields.
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        help_text="Product category",
    )
    name = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Full product title (e.g. 'NovaBook Pro 16-inch')",
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        db_index=True,
        help_text="URL slug (e.g. 'novabook-pro-16-inch')",
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short marketing punchline (e.g. 'Mind-blowing. Head-turning.')",
    )
    description = models.TextField(
        help_text="Detailed product description and marketing highlights",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Current selling price in INR (₹)",
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Original MRP for showing savings/discounts (optional)",
    )
    image = models.ImageField(
        upload_to="products/%Y/%m/",
        help_text="Primary product photography",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Only active products are visible in public storefront",
    )
    is_featured = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Feature this product on homepage and prominent banners",
    )
    stock = models.PositiveIntegerField(
        default=10,
        help_text="Inventory quantity currently available",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        verbose_name = "Product"
        verbose_name_plural = "Products"
        indexes = [
            models.Index(fields=["is_active", "is_featured"]),
            models.Index(fields=["category", "is_active"]),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:product_detail", kwargs={"slug": self.slug})

    @property
    def formatted_price(self):
        """Format price with Indian numbering comma system (e.g. ₹1,49,900)."""
        amount = int(round(self.price))
        s = str(amount)
        if len(s) <= 3:
            return f"₹{s}"
        last_three = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        return f"₹{','.join(groups)},{last_three}"

    @property
    def formatted_original_price(self):
        """Format original MRP if present."""
        if not self.original_price:
            return None
        amount = int(round(self.original_price))
        s = str(amount)
        if len(s) <= 3:
            return f"₹{s}"
        last_three = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        return f"₹{','.join(groups)},{last_three}"

    @property
    def discount_percent(self):
        """Calculate discount percentage if original price is greater than price."""
        if self.original_price and self.original_price > self.price:
            savings = self.original_price - self.price
            return int(round((savings / self.original_price) * 100))
        return 0

    def image_preview_thumb(self):
        """Thumbnail preview for admin list view."""
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" style="width: 50px; height: 50px; object-fit: contain; background: #fff; border-radius: 4px; border: 1px solid #eee; padding: 2px;" />'
            )
        return "No Image"
    image_preview_thumb.short_description = "Image"

    def image_preview_large(self):
        """Large preview for admin edit view."""
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" style="max-width: 320px; height: auto; border-radius: 8px; border: 1px solid #ddd; padding: 6px; background: #fff; margin-top: 8px;" />'
            )
        return "No Image Uploaded"
    image_preview_large.short_description = "Image Preview"


class ProductSpecification(models.Model):
    """
    Key technical specifications for electronics (Processor, Display, RAM, Storage, Battery, etc.).
    Managed seamlessly via Django Admin TabularInlines inside the Product editor.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="specifications",
    )
    name = models.CharField(
        max_length=100,
        help_text="Spec label (e.g. 'Processor', 'Display', 'Battery Life')",
    )
    value = models.CharField(
        max_length=255,
        help_text="Spec detail (e.g. 'NovaSilicon M3 Max, 16-Core CPU', 'Liquid OLED 120Hz')",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order in which this spec is listed",
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Product Specification"
        verbose_name_plural = "Product Specifications"

    def __str__(self):
        return f"{self.name}: {self.value}"
