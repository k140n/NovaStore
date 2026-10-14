from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from catalog.models import Category, Product
from .models import Banner

User = get_user_model()


class CoreViewsTest(TestCase):
    def setUp(self):
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
            b"\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00"
            b"\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
        )
        self.test_img = SimpleUploadedFile("test.gif", small_gif, content_type="image/gif")

        # Banners
        self.active_banner = Banner.objects.create(
            title="NovaBook Special Banner",
            subtitle="Headline for testing",
            image=self.test_img,
            order=1,
            is_active=True,
        )
        self.inactive_banner = Banner.objects.create(
            title="Secret Inactive Banner",
            image=self.test_img,
            order=2,
            is_active=False,
        )

        # Categories
        self.category = Category.objects.create(
            name="Laptops",
            slug="laptops",
            is_active=True,
            order=1,
        )
        self.inactive_category = Category.objects.create(
            name="Hidden Category",
            slug="hidden-category",
            is_active=False,
            order=2,
        )

        # Products
        self.featured_product = Product.objects.create(
            category=self.category,
            name="NovaBook Pro Max Test",
            slug="novabook-pro-max-test",
            tagline="Extreme Pro Power",
            price=Decimal("199900.00"),
            image=self.test_img,
            is_active=True,
            is_featured=True,
        )
        self.inactive_product = Product.objects.create(
            category=self.category,
            name="Secret Prototype Device",
            slug="secret-prototype",
            price=Decimal("999900.00"),
            image=self.test_img,
            is_active=False,
            is_featured=True,
        )

    def test_home_page_status_code(self):
        """Verify the home page loads successfully with HTTP 200."""
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template_used(self):
        """Verify correct template hierarchy is rendered."""
        response = self.client.get(reverse("core:home"))
        self.assertTemplateUsed(response, "core/home.html")
        self.assertTemplateUsed(response, "base.html")

    def test_home_page_content_and_branding(self):
        """Verify the brand name is present in response."""
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "NovaStore")

    def test_home_page_displays_active_banners_only(self):
        """Only active banners should be present in public homepage."""
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "NovaBook Special Banner")
        self.assertNotContains(response, "Secret Inactive Banner")

    def test_home_page_displays_featured_products_only(self):
        """Featured active products must appear, but inactive products must not."""
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "NovaBook Pro Max Test")
        self.assertContains(response, "₹1,99,900")
        self.assertNotContains(response, "Secret Prototype Device")

    def test_home_page_displays_active_categories(self):
        """Active categories appear in nav and category ribbon, inactive do not."""
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Laptops")
        self.assertNotContains(response, "Hidden Category")

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


class CoreEdgeCasesAndAdminTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="testadmin",
            email="admin@novastore.local",
            password="AdminPassword123!",
        )

    def test_home_page_empty_database_renders_gracefully(self):
        """Home page must render cleanly with HTTP 200 even with an empty database."""
        Banner.objects.all().delete()
        Category.objects.all().delete()
        Product.objects.all().delete()
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NovaStore")

    def test_custom_404_preview_page(self):
        """Custom 404 page renders branded Apple-style layout."""
        response = self.client.get("/404/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(response, "The page you're looking for can't be found.", status_code=404)

    def test_custom_500_preview_page(self):
        """Custom 500 page renders branded Apple-style layout."""
        response = self.client.get("/500/")
        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(response, "500.html")
        self.assertContains(response, "We are experiencing technical difficulties.", status_code=500)

    def test_banner_admin_crud_access(self):
        """Staff/admin can access Banner change list in Django Admin."""
        self.client.login(username="testadmin", password="AdminPassword123!")
        response = self.client.get("/admin/core/banner/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NovaStore Administration")


class SecurityAndAccessibilityTest(TestCase):
    def test_security_headers_present(self):
        """Responses must include clickjacking and MIME-sniffing prevention headers."""
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")

    def test_skip_link_rendered(self):
        """A keyboard-accessible skip-to-content link must be present on page."""
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, '<a href="#main-content" class="skip-link">Skip to main content</a>')

    def test_csrf_token_on_auth_forms(self):
        """Authentication forms must include CSRF tokens for security."""
        reg_response = self.client.get(reverse("accounts:register"))
        self.assertContains(reg_response, "csrfmiddlewaretoken")

        login_response = self.client.get(reverse("accounts:login"))
        self.assertContains(login_response, "csrfmiddlewaretoken")

    def test_heading_structure_single_h1_on_home(self):
        """Home page should maintain a single primary <h1> element for WCAG compliance."""
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        h1_count = content.count("<h1")
        self.assertEqual(h1_count, 1)

