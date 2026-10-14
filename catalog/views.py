from django.shortcuts import get_object_or_404, render
from .models import Category, Product


def product_list_view(request):
    """
    Catalogue listing view with category filtering, search, and ordering.
    Will be fully detailed in Milestone 4.
    """
    category_slug = request.GET.get("category")
    search_query = request.GET.get("q", "").strip()

    products = Product.objects.active().select_related("category")
    selected_category = None

    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=selected_category)

    if search_query:
        products = products.filter(name__icontains=search_query)

    categories = Category.objects.active()

    return render(request, "catalog/product_list.html", {
        "products": products,
        "categories": categories,
        "selected_category": selected_category,
        "search_query": search_query,
    })


def category_detail_view(request, slug):
    """
    Category-specific product listing view.
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = category.products.filter(is_active=True)
    categories = Category.objects.active()

    return render(request, "catalog/product_list.html", {
        "products": products,
        "categories": categories,
        "selected_category": category,
    })


def product_detail_view(request, slug):
    """
    Individual product detail page showing specifications, imagery, and pricing.
    """
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("specifications"),
        slug=slug,
        is_active=True,
    )
    related_products = (
        Product.objects.active()
        .filter(category=product.category)
        .exclude(id=product.id)[:4]
    )

    return render(request, "catalog/product_detail.html", {
        "product": product,
        "related_products": related_products,
    })
