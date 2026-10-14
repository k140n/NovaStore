from .models import Category

def category_navigation(request):
    """
    Exposes active categories across all templates for dynamic header navigation and footer links.
    """
    return {
        "nav_categories": Category.objects.active()[:8],
    }
