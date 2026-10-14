from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from .forms import UserLoginForm, UserProfileUpdateForm, UserRegistrationForm


def register_view(request):
    """
    Handle new user registration. If already logged in, redirect to profile.
    """
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(
                request,
                f"Welcome to NovaStore, {user.first_name or user.username}! Your Nova Account has been created.",
            )
            return redirect("accounts:profile")
        else:
            messages.error(request, "Please correct the errors indicated below.")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {
        "page_title": "Create Your Nova ID — NovaStore",
        "form": form,
    })


def login_view(request):
    """
    Handle user sign in with session authentication and redirect handling.
    """
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    redirect_to = request.POST.get("next") or request.GET.get("next") or "accounts:profile"

    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Signed in successfully. Welcome back, {user.first_name or user.username}!")
            return redirect(redirect_to)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm(request)

    return render(request, "accounts/login.html", {
        "page_title": "Sign In with Nova ID — NovaStore",
        "form": form,
        "next": redirect_to,
    })


def logout_view(request):
    """
    Handle user sign out with confirmation message.
    """
    if request.user.is_authenticated:
        auth_logout(request)
        messages.info(request, "You have been safely signed out of your Nova Account.")
    return redirect("core:home")


@login_required(login_url="accounts:login")
def profile_view(request):
    """
    Protected user profile dashboard allowing personal details update and
    viewing associated account information.
    """
    if request.method == "POST" and "update_profile" in request.POST:
        profile_form = UserProfileUpdateForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Your account details have been updated successfully.")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Please resolve the errors below to update your profile.")
    else:
        profile_form = UserProfileUpdateForm(instance=request.user)

    password_form = PasswordChangeForm(user=request.user)

    # Simulated registered devices for Apple-style account hub
    user_devices = [
        {"name": "NovaBook Pro 16", "type": "Laptop", "os": "NovaOS Sonoma", "status": "Active & Protected"},
        {"name": "NovaPhone 16 Pro", "type": "Smartphone", "os": "NovaOS 18.2", "status": "Active & Protected"},
    ]

    return render(request, "accounts/profile.html", {
        "page_title": f"My Nova Account — {request.user.username}",
        "profile_form": profile_form,
        "password_form": password_form,
        "user_devices": user_devices,
    })


@login_required(login_url="accounts:login")
def change_password_view(request):
    """
    Handle secure password change with session continuity.
    """
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Prevent logging the user out after their password is changed
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Failed to update password. Please check the requirements below.")
            profile_form = UserProfileUpdateForm(instance=request.user)
            return render(request, "accounts/profile.html", {
                "page_title": f"My Nova Account — {request.user.username}",
                "profile_form": profile_form,
                "password_form": form,
                "active_tab": "security",
            })

    return redirect("accounts:profile")
