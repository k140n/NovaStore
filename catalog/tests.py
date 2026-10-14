from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from .models import Category, Product, ProductSpecification


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Laptops",
            slug="laptops",
            description="Ultraportable laptops and workstations",
            order=1,
            is_active=True,
        )
        self.inactive_category = Category.objects.create(
            name="Legacy Accessories",
            slug="legacy-accessories",
            order=2,
            is_active=False,
        )

    def test_category_string_representation(self):
        self.assertEqual(str(self.category), "Laptops")

    def test_active_categories_manager(self):
        active_cats = Category.objects.active()
        self.assertIn(self.category, active_cats)
        self.assertNotIn(self.inactive_category, active_cats)

    def test_product_count_helper(self):
        self.assertEqual(self.category.product_count(), 0)
        # Create 1 active and 1 inactive product
        Product.objects.create(
            category=self.category,
            name="NovaBook 14",
            slug="novabook-14",
            price=Decimal("99990.00"),
            is_active=True,
        )
        Product.objects.create(
            category=self.category,
            name="NovaBook 14 Prototype",
            slug="novabook-14-proto",
            price=Decimal("99990.00"),
            is_active=False,
        )
        # Only active products should count
        self.assertEqual(self.category.product_count(), 1)


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Smartphones",
            slug="smartphones",
        )
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
            b"\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00"
            b"\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
        )
        self.test_image = SimpleUploadedFile(
            "test_phone.gif", small_gif, content_type="image/gif"
        )
        self.product = Product.objects.create(
            category=self.category,
            name="NovaPhone 16 Pro",
            slug="novaphone-16-pro",
            tagline="Titanium. So strong. So Pro.",
            description="Super Retina XDR OLED with ProMotion.",
            price=Decimal("134900.00"),
            original_price=Decimal("144900.00"),
            image=self.test_image,
            is_active=True,
            is_featured=True,
            stock=15,
        )
        self.inactive_product = Product.objects.create(
            category=self.category,
            name="NovaPhone Discontinued",
            slug="novaphone-discontinued",
            price=Decimal("49900.00"),
            is_active=False,
            is_featured=False,
        )

    def test_product_string_representation(self):
        self.assertEqual(str(self.product), "NovaPhone 16 Pro")

    def test_active_manager_filters(self):
        active_products = Product.objects.active()
        self.assertIn(self.product, active_products)
        self.assertNotIn(self.inactive_product, active_products)

    def test_featured_manager_filters(self):
        featured_products = Product.objects.featured()
        self.assertIn(self.product, featured_products)
        self.assertNotIn(self.inactive_product, featured_products)

    def test_price_formatting_indian_rupee(self):
        self.assertEqual(self.product.formatted_price, "₹1,34,900")
        self.assertEqual(self.product.formatted_original_price, "₹1,44,900")

    def test_discount_calculation(self):
        self.assertEqual(self.product.discount_percent, 7)

    def test_product_specifications_relationship(self):
        spec1 = ProductSpecification.objects.create(
            product=self.product,
            name="Chip",
            value="NovaSilicon A18 Pro",
            order=1,
        )
        spec2 = ProductSpecification.objects.create(
            product=self.product,
            name="Display",
            value="6.7-inch Super Retina XDR",
            order=2,
        )
        self.assertEqual(self.product.specifications.count(), 2)
        specs = list(self.product.specifications.all())
        self.assertEqual(specs[0].name, "Chip")
        self.assertEqual(specs[1].name, "Display")


class CatalogViewsTest(TestCase):
    def setUp(self):
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
            b"\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00"
            b"\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
        )
        self.test_img = SimpleUploadedFile("test_view.gif", small_gif, content_type="image/gif")

        self.cat_laptops = Category.objects.create(name="Laptops", slug="laptops", is_active=True, order=1)
        self.cat_audio = Category.objects.create(name="Audio", slug="audio", is_active=True, order=2)

        # Products
        self.laptop = Product.objects.create(
            category=self.cat_laptops,
            name="NovaBook Pro 16",
            slug="novabook-pro-16",
            tagline="Extreme Pro Power",
            description="M3 Max chip workstation.",
            price=Decimal("249900.00"),
            original_price=Decimal("269900.00"),
            image=self.test_img,
            is_active=True,
            is_featured=True,
            stock=10,
        )
        self.audio = Product.objects.create(
            category=self.cat_audio,
            name="NovaPods Max",
            slug="novapods-max",
            tagline="Pure Sound",
            description="Active noise cancellation headphones.",
            price=Decimal("59900.00"),
            image=self.test_img,
            is_active=True,
            is_featured=False,
            stock=20,
        )
        self.inactive_item = Product.objects.create(
            category=self.cat_laptops,
            name="Unreleased Prototype Laptop",
            slug="unreleased-prototype",
            price=Decimal("999900.00"),
            image=self.test_img,
            is_active=False,
        )

        ProductSpecification.objects.create(
            product=self.laptop,
            name="Processor",
            value="NovaSilicon M3 Max",
            order=1,
        )

    def test_product_list_view_renders_ok(self):
        """Verify the catalog list loads successfully with HTTP 200."""
        response = self.client.get(reverse("catalog:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_list.html")
        self.assertContains(response, "NovaBook Pro 16")
        self.assertContains(response, "NovaPods Max")

    def test_product_list_category_filtering(self):
        """Verify filtering by category includes matching items and excludes others."""
        response = self.client.get(reverse("catalog:product_list") + "?category=laptops")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NovaBook Pro 16")
        self.assertNotContains(response, "NovaPods Max")

    def test_product_list_search_by_name(self):
        """Verify keyword search returns matching products and excludes non-matching."""
        response = self.client.get(reverse("catalog:product_list") + "?q=NovaPods")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NovaPods Max")
        self.assertNotContains(response, "NovaBook Pro 16")

    def test_product_list_sorting_price(self):
        """Verify sort=price_low returns cheaper products first."""
        response = self.client.get(reverse("catalog:product_list") + "?sort=price_low")
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertEqual(products[0], self.audio)  # ₹59,900
        self.assertEqual(products[1], self.laptop) # ₹2,49,900

    def test_inactive_products_never_appear_in_catalog(self):
        """Public catalog must strictly hide inactive products."""
        response = self.client.get(reverse("catalog:product_list"))
        self.assertNotContains(response, "Unreleased Prototype Laptop")

        # Also search should not reveal inactive items
        search_res = self.client.get(reverse("catalog:product_list") + "?q=Prototype")
        self.assertNotContains(search_res, "Unreleased Prototype Laptop")

    def test_product_detail_view_success(self):
        """Detail page should load with HTTP 200, product info, and technical specifications."""
        response = self.client.get(reverse("catalog:product_detail", kwargs={"slug": self.laptop.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_detail.html")
        self.assertContains(response, "NovaBook Pro 16")
        self.assertContains(response, "₹2,49,900")
        self.assertContains(response, "NovaSilicon M3 Max")

    def test_product_detail_inactive_returns_404(self):
        """Visiting an inactive product URL directly must return HTTP 404."""
        response = self.client.get(reverse("catalog:product_detail", kwargs={"slug": self.inactive_item.slug}))
        self.assertEqual(response.status_code, 404)

    def test_product_detail_nonexistent_returns_404(self):
        """Visiting a nonexistent slug must return HTTP 404."""
        response = self.client.get(reverse("catalog:product_detail", kwargs={"slug": "non-existent-device-xyz"}))
        self.assertEqual(response.status_code, 404)

    def test_category_shortcut_view(self):
        """Category detail URL routes properly."""
        response = self.client.get(reverse("catalog:category_detail", kwargs={"slug": "laptops"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NovaBook Pro 16")
