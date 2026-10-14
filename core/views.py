from django.shortcuts import render

def home_view(request):
    """
    Initial home view for NovaStore.
    Will be fully expanded in Milestone 3 with banners, categories, and featured products.
    """
    return render(request, "core/home.html", {
        "page_title": "NovaStore — Next-Generation Electronics",
    })
