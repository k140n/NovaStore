from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from .models import Category, Product


def product_list_view(request):
    """
    Main product catalog view with category filtering, live text search,
    sorting, and pagination. Only active products are visible.
    """
    category_slug = request.GET.get("category", "").strip()
    search_query = request.GET.get("q", "").strip()
    sort_option = request.GET.get("sort", "featured").strip()

    products = (
        Product.objects.active()
        .select_related("category")
        .prefetch_related("specifications")
    )
    selected_category = None

    # 1. Category Filtering
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=selected_category)

    # 2. Search by Name, Tagline, or Description
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(tagline__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    # 3. Sorting
    if sort_option == "price_low":
        products = products.order_by("price")
    elif sort_option == "price_high":
        products = products.order_by("-price")
    elif sort_option == "newest":
        products = products.order_by("-created_at")
    else:  # 'featured' default
        products = products.order_by("-is_featured", "-created_at")

    total_results = products.count()

    # 4. Pagination (6 products per page for clear pagination demonstration)
    paginator = Paginator(products, 6)
    page_number = request.GET.get("page", 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    categories = Category.objects.active()

    context = {
        "page_title": (
            f"{selected_category.name} — NovaStore"
            if selected_category
            else "Explore All Products — NovaStore"
        ),
        "products": page_obj,
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": selected_category,
        "search_query": search_query,
        "current_sort": sort_option,
        "total_results": total_results,
    }
    return render(request, "catalog/product_list.html", context)


def category_detail_view(request, slug):
    """
    Category-specific shortcut view that delegates directly to product_list_view
    for consistent filtering, search, and pagination.
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)
    # Forward to product_list with category context
    request.GET = request.GET.copy()
    request.GET["category"] = category.slug
    return product_list_view(request)


def product_detail_view(request, slug):
    """
    Individual product detail page showing rich hardware imagery,
    technical specifications breakdown, stock availability, and related items.
    """
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("specifications"),
        slug=slug,
        is_active=True,
    )

    # Related items within the same category
    related_products = (
        Product.objects.active()
        .filter(category=product.category)
        .exclude(id=product.id)
        .select_related("category")[:4]
    )

    context = {
        "page_title": f"{product.name} — NovaStore",
        "product": product,
        "specifications": product.specifications.all(),
        "related_products": related_products,
    }
    return render(request, "catalog/product_detail.html", context)
