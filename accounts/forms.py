from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    """
    Form for registering a new NovaStore user with secure password validation.
    """
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "First name",
            "autocomplete": "given-name",
        }),
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "Last name",
            "autocomplete": "family-name",
        }),
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "Username (e.g. alex2026)",
            "autocomplete": "username",
        }),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "auth-input",
            "placeholder": "name@example.com",
            "autocomplete": "email",
        }),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            "class": "auth-input",
            "placeholder": "Password (8+ chars, numbers & letters)",
            "autocomplete": "new-password",
        }),
        help_text="Password must be at least 8 characters and meet standard complexity requirements.",
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            "class": "auth-input",
            "placeholder": "Confirm password",
            "autocomplete": "new-password",
        }),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]

    def clean_email(self):
        email = self.cleaned_data.get("email").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A Nova Account is already registered with this email address.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username").strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                self.add_error("confirm_password", "Passwords do not match. Please re-enter.")
            else:
                # Validate against Django's configured password validators
                try:
                    validate_password(password)
                except ValidationError as e:
                    self.add_error("password", e)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """
    Styled login form for NovaStore authentication.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "Username or Email",
            "autocomplete": "username",
            "autofocus": True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "auth-input",
            "placeholder": "Password",
            "autocomplete": "current-password",
        })
    )


class UserProfileUpdateForm(forms.ModelForm):
    """
    Form allowing users to update their personal profile info.
    """
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "auth-input", "placeholder": "First name"}),
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "auth-input", "placeholder": "Last name"}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "auth-input", "placeholder": "Email address"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get("instance")
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email").strip().lower()
        if (
            self.user
            and User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists()
        ):
            raise ValidationError("This email address is already in use by another account.")
        return email
