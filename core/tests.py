from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from .models import Banner

User = get_user_model()


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

    def test_admin_redirect_or_login(self):
        """Verify admin portal redirects unauthenticated users."""
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)


class BannerModelTest(TestCase):
    def setUp(self):
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
            b"\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00"
            b"\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
        )
        self.banner_img = SimpleUploadedFile("hero.gif", small_gif, content_type="image/gif")
        self.active_banner_1 = Banner.objects.create(
            title="MacBook Pro",
            subtitle="Mind-blowing. Head-turning.",
            image=self.banner_img,
            order=2,
            is_active=True,
        )
        self.active_banner_0 = Banner.objects.create(
            title="iPhone 16 Pro",
            subtitle="Hello, Apple Intelligence.",
            image=self.banner_img,
            order=1,
            is_active=True,
        )
        self.inactive_banner = Banner.objects.create(
            title="Old Campaign Banner",
            image=self.banner_img,
            order=0,
            is_active=False,
        )

    def test_banner_str(self):
        self.assertEqual(str(self.active_banner_0), "iPhone 16 Pro")

    def test_active_banner_filtering_and_order(self):
        banners = list(Banner.objects.active())
        self.assertEqual(len(banners), 2)
        # Order 1 should come before order 2
        self.assertEqual(banners[0], self.active_banner_0)
        self.assertEqual(banners[1], self.active_banner_1)
        self.assertNotIn(self.inactive_banner, banners)

    def test_banner_image_preview_methods(self):
        self.assertIn("<img", self.active_banner_0.image_preview_thumb())
        self.assertIn("<img", self.active_banner_0.image_preview_large())
