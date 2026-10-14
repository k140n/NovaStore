from django.shortcuts import render, redirect

def login_view(request):
    """Placeholder view for login, detailed in Milestone 5."""
    return render(request, "accounts/login.html", {})

def register_view(request):
    """Placeholder view for register, detailed in Milestone 5."""
    return render(request, "accounts/register.html", {})

def profile_view(request):
    """Placeholder view for profile, detailed in Milestone 5."""
    return render(request, "accounts/profile.html", {})

def logout_view(request):
    """Placeholder view for logout, detailed in Milestone 5."""
    return redirect("core:home")
