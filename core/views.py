from django.shortcuts import render
from catalog.models import Category, Product
from core.models import Banner


def home_view(request):
    """
    Homepage view for NovaStore.
    Loads active hero banners, categories, featured products, and latest releases dynamically.
    """
    banners = Banner.objects.active()
    categories = Category.objects.active()
    featured_products = Product.objects.featured().select_related("category")[:8]
    latest_products = Product.objects.active().select_related("category").order_by("-created_at")[:4]

    context = {
        "page_title": "NovaStore — Next-Generation Electronics Store",
        "banners": banners,
        "categories": categories,
        "featured_products": featured_products,
        "latest_products": latest_products,
    }
    return render(request, "core/home.html", context)
