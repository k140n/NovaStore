from django.test import TestCase
from django.urls import reverse


class CoreViewsTest(TestCase):
    def test_home_page_status_code(self):
        """Verify the home page loads successfully with HTTP 200."""
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template_used(self):
        """Verify correct template hierarchy is rendered."""
        response = self.client.get(reverse("core:home"))
        self.assertTemplateUsed(response, "core/home.html")
        self.assertTemplateUsed(response, "base.html")

    def test_home_page_content(self):
        """Verify the brand name and title are present in response."""
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "NovaStore")
        self.assertContains(response, "Engineering the Future of Electronics")

    def test_admin_redirect_or_login(self):
        """Verify admin portal is accessible."""
        response = self.client.get("/admin/")
        # Django admin redirects to login when unauthenticated
        self.assertEqual(response.status_code, 302)
