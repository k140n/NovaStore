from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@novastore.local",
            password="SecurePassword123!",
            first_name="Test",
            last_name="User",
        )

    def test_registration_view_get(self):
        """Registration page loads with HTTP 200."""
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_registration_successful(self):
        """User registers with valid data, is automatically logged in and redirected to profile."""
        data = {
            "first_name": "Kiran",
            "last_name": "Dev",
            "username": "kirandev",
            "email": "kiran@example.com",
            "password": "StrongPassword2026!",
            "confirm_password": "StrongPassword2026!",
        }
        response = self.client.post(reverse("accounts:register"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")
        # Verify user exists in database
        self.assertTrue(User.objects.filter(username="kirandev").exists())
        # Verify authenticated session
        self.assertEqual(int(self.client.session["_auth_user_id"]), User.objects.get(username="kirandev").pk)

    def test_registration_password_mismatch(self):
        """Password mismatch triggers validation error and does not create user."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "john@example.com",
            "password": "PasswordOne123!",
            "confirm_password": "PasswordDifferent123!",
        }
        response = self.client.post(reverse("accounts:register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="johndoe").exists())
        self.assertFormError(response.context["form"], "confirm_password", "Passwords do not match. Please re-enter.")

    def test_registration_duplicate_username(self):
        """Cannot register with an existing username."""
        data = {
            "first_name": "Another",
            "last_name": "User",
            "username": "testuser",  # Already exists
            "email": "another@example.com",
            "password": "StrongPassword2026!",
            "confirm_password": "StrongPassword2026!",
        }
        response = self.client.post(reverse("accounts:register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "username", "This username is already taken. Please choose another.")

    def test_registration_duplicate_email(self):
        """Cannot register with an existing email address."""
        data = {
            "first_name": "Another",
            "last_name": "User",
            "username": "uniqueusername",
            "email": "testuser@novastore.local",  # Already exists
            "password": "StrongPassword2026!",
            "confirm_password": "StrongPassword2026!",
        }
        response = self.client.post(reverse("accounts:register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "email", "A Nova Account is already registered with this email address.")

    def test_login_view_get(self):
        """Login page loads with HTTP 200."""
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_successful(self):
        """Valid credentials log the user in and redirect to profile."""
        response = self.client.post(reverse("accounts:login"), {
            "username": "testuser",
            "password": "SecurePassword123!",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_login_invalid_password(self):
        """Incorrect password fails login and displays error."""
        response = self.client.post(reverse("accounts:login"), {
            "username": "testuser",
            "password": "WrongPassword123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(response, "Invalid username or password")

    def test_logout(self):
        """Logout clears the user session and redirects to home."""
        self.client.login(username="testuser", password="SecurePassword123!")
        response = self.client.get(reverse("accounts:logout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTemplateUsed(response, "core/home.html")

    def test_profile_protected_requires_login(self):
        """Accessing profile while unauthenticated redirects to login."""
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_profile_accessible_when_authenticated(self):
        """Authenticated user can view profile."""
        self.client.login(username="testuser", password="SecurePassword123!")
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")
        self.assertContains(response, "testuser@novastore.local")

    def test_profile_update_successful(self):
        """User can update their personal details."""
        self.client.login(username="testuser", password="SecurePassword123!")
        data = {
            "update_profile": "1",
            "first_name": "UpdatedFirst",
            "last_name": "UpdatedLast",
            "email": "updated@novastore.local",
        }
        response = self.client.post(reverse("accounts:profile"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "UpdatedFirst")
        self.assertEqual(self.user.last_name, "UpdatedLast")
        self.assertEqual(self.user.email, "updated@novastore.local")

    def test_password_change_successful(self):
        """User can change password securely."""
        self.client.login(username="testuser", password="SecurePassword123!")
        data = {
            "old_password": "SecurePassword123!",
            "new_password1": "BrandNewPassword2026!",
            "new_password2": "BrandNewPassword2026!",
        }
        response = self.client.post(reverse("accounts:password_change"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Verify user can log in with new password
        self.assertTrue(self.client.login(username="testuser", password="BrandNewPassword2026!"))

    def test_login_with_next_parameter_redirects_correctly(self):
        """Successful login redirects user back to intended destination via 'next' query param."""
        response = self.client.post(
            reverse("accounts:login") + "?next=/catalog/",
            {"username": "testuser", "password": "SecurePassword123!"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("/catalog/", response.request["PATH_INFO"])

    def test_login_inactive_user_cannot_login(self):
        """Inactive user account cannot authenticate."""
        self.user.is_active = False
        self.user.save()
        response = self.client.post(reverse("accounts:login"), {
            "username": "testuser",
            "password": "SecurePassword123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(response, "Invalid username or password")

    def test_login_nonexistent_user(self):
        """Nonexistent username cannot authenticate."""
        response = self.client.post(reverse("accounts:login"), {
            "username": "ghostuser",
            "password": "SomePassword123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_profile_update_duplicate_email_rejected(self):
        """User cannot update their email to one already registered by another account."""
        User.objects.create_user(username="seconduser", email="second@novastore.local", password="Password123!")
        self.client.login(username="testuser", password="SecurePassword123!")
        data = {
            "update_profile": "1",
            "first_name": "Test",
            "last_name": "User",
            "email": "second@novastore.local",
        }
        response = self.client.post(reverse("accounts:profile"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["profile_form"], "email", "This email address is already in use by another account.")

    def test_password_change_unauthenticated_redirects(self):
        """Unauthenticated user accessing password change is redirected to login."""
        response = self.client.get(reverse("accounts:password_change"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_password_change_incorrect_old_password(self):
        """Password change fails if the current password is wrong."""
        self.client.login(username="testuser", password="SecurePassword123!")
        data = {
            "old_password": "WrongPassword999!",
            "new_password1": "NewSecret2026!",
            "new_password2": "NewSecret2026!",
        }
        response = self.client.post(reverse("accounts:password_change"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("old_password", response.context["password_form"].errors)

    def test_password_change_mismatched_new_passwords(self):
        """Password change fails if confirmation password does not match."""
        self.client.login(username="testuser", password="SecurePassword123!")
        data = {
            "old_password": "SecurePassword123!",
            "new_password1": "NewSecret2026!",
            "new_password2": "MismatchSecret2026!",
        }
        response = self.client.post(reverse("accounts:password_change"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("new_password2", response.context["password_form"].errors)

    def test_password_change_maintains_login_session(self):
        """Changing password updates session hash so the user remains logged in without disruption."""
        self.client.login(username="testuser", password="SecurePassword123!")
        data = {
            "old_password": "SecurePassword123!",
            "new_password1": "BrandNewSecret2026!",
            "new_password2": "BrandNewSecret2026!",
        }
        response = self.client.post(reverse("accounts:password_change"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)
