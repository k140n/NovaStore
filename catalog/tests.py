from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from catalog.context_processors import category_navigation
from .models import Category, Product, ProductSpecification

User = get_user_model()


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

    def test_category_unique_slug_enforced(self):
        """Database IntegrityError raised if slug is duplicate."""
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Another Laptops", slug="laptops")


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

    def test_product_unique_slug_enforced(self):
        """Database IntegrityError raised if product slug is duplicate."""
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                category=self.category,
                name="Duplicate Slug Device",
                slug="novaphone-16-pro",
                price=Decimal("999.00"),
                image=self.test_image,
            )

    def test_price_formatting_indian_rupee(self):
        self.assertEqual(self.product.formatted_price, "₹1,34,900")
        self.assertEqual(self.product.formatted_original_price, "₹1,44,900")

    def test_price_formatting_various_denominations(self):
        """Test Indian currency comma system for hundreds, thousands, and lakhs."""
        p1 = Product(category=self.category, name="P1", slug="p1", price=Decimal("499.00"))
        self.assertEqual(p1.formatted_price, "₹499")

        p2 = Product(category=self.category, name="P2", slug="p2", price=Decimal("1499.00"))
        self.assertEqual(p2.formatted_price, "₹1,499")

        p3 = Product(category=self.category, name="P3", slug="p3", price=Decimal("49999.00"))
        self.assertEqual(p3.formatted_price, "₹49,999")

        p4 = Product(category=self.category, name="P4", slug="p4", price=Decimal("1549900.00"))
        self.assertEqual(p4.formatted_price, "₹15,49,900")

    def test_discount_calculation(self):
        self.assertEqual(self.product.discount_percent, 7)

    def test_discount_calculation_edge_cases(self):
        """Discount should be 0 when no original_price or original_price <= price."""
        p_no_orig = Product(category=self.category, name="NoOrig", slug="no-orig", price=Decimal("50000.00"))
        self.assertEqual(p_no_orig.discount_percent, 0)
        self.assertIsNone(p_no_orig.formatted_original_price)

        p_equal = Product(category=self.category, name="Equal", slug="equal", price=Decimal("50000.00"), original_price=Decimal("50000.00"))
        self.assertEqual(p_equal.discount_percent, 0)

        p_cheaper_orig = Product(category=self.category, name="CheapOrig", slug="cheap-orig", price=Decimal("50000.00"), original_price=Decimal("40000.00"))
        self.assertEqual(p_cheaper_orig.discount_percent, 0)

    def test_product_specifications_relationship_and_str(self):
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
        self.assertEqual(str(spec1), "Chip: NovaSilicon A18 Pro")
        self.assertEqual(self.product.specifications.count(), 2)
        specs = list(self.product.specifications.all())
        self.assertEqual(specs[0].name, "Chip")
        self.assertEqual(specs[1].name, "Display")

    def test_image_preview_helpers(self):
        """Test image preview HTML tags and fallback text when image is missing."""
        self.assertIn("<img", self.product.image_preview_thumb())
        self.assertIn("<img", self.product.image_preview_large())

        p_no_img = Product(category=self.category, name="NoImg", slug="no-img", price=Decimal("100.00"))
        self.assertEqual(p_no_img.image_preview_thumb(), "No Image")
        self.assertEqual(p_no_img.image_preview_large(), "No Image Uploaded")


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

    def test_product_list_sorting_price_high(self):
        """Verify sort=price_high returns most expensive products first."""
        response = self.client.get(reverse("catalog:product_list") + "?sort=price_high")
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertEqual(products[0], self.laptop)  # ₹2,49,900
        self.assertEqual(products[1], self.audio)   # ₹59,900

    def test_product_list_sorting_featured(self):
        """Verify sort=featured places featured products first."""
        response = self.client.get(reverse("catalog:product_list") + "?sort=featured")
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertTrue(products[0].is_featured)

    def test_product_list_pagination_multiple_pages(self):
        """Verify 6-per-page pagination handles multiple pages accurately."""
        # Create 7 extra laptops (total 8 laptops in cat_laptops)
        for i in range(7):
            Product.objects.create(
                category=self.cat_laptops,
                name=f"NovaBook Mini {i}",
                slug=f"novabook-mini-{i}",
                price=Decimal("69900.00"),
                image=self.test_img,
                is_active=True,
            )
        # Page 1 should contain 6 items
        resp1 = self.client.get(reverse("catalog:product_list") + "?category=laptops&page=1")
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(len(resp1.context["products"]), 6)
        self.assertTrue(resp1.context["products"].has_next())

        # Page 2 should contain the remaining 2 items
        resp2 = self.client.get(reverse("catalog:product_list") + "?category=laptops&page=2")
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(resp2.context["products"]), 2)
        self.assertFalse(resp2.context["products"].has_next())

    def test_product_list_pagination_invalid_page_falls_back(self):
        """Invalid page parameter gracefully defaults to page 1."""
        response = self.client.get(reverse("catalog:product_list") + "?page=not-a-number")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["products"].number, 1)

    def test_product_list_pagination_out_of_range_delivers_last(self):
        """Page number beyond total pages delivers the final page."""
        response = self.client.get(reverse("catalog:product_list") + "?page=9999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["products"].number, 1)

    def test_product_list_search_description_and_tagline(self):
        """Search query matches against product description and tagline text."""
        # Match by description keyword
        resp_desc = self.client.get(reverse("catalog:product_list") + "?q=workstation")
        self.assertContains(resp_desc, "NovaBook Pro 16")
        self.assertNotContains(resp_desc, "NovaPods Max")

        # Match by tagline keyword
        resp_tag = self.client.get(reverse("catalog:product_list") + "?q=Extreme")
        self.assertContains(resp_tag, "NovaBook Pro 16")

    def test_product_list_search_whitespace_trimmed(self):
        """Search handles leading and trailing whitespace cleanly."""
        response = self.client.get(reverse("catalog:product_list") + "?q=   NovaPods   ")
        self.assertContains(response, "NovaPods Max")

    def test_product_list_search_no_results_empty_state(self):
        """Search yielding zero results renders empty state message."""
        response = self.client.get(reverse("catalog:product_list") + "?q=NonExistentGadgetXYZ")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["products"]), 0)
        self.assertContains(response, "No matching products found")

    def test_product_detail_related_products_logic(self):
        """Related products section displays up to 4 active products from same category, excluding self."""
        # Create second active laptop
        laptop2 = Product.objects.create(
            category=self.cat_laptops,
            name="NovaBook Air 13",
            slug="novabook-air-13",
            price=Decimal("99900.00"),
            image=self.test_img,
            is_active=True,
        )
        response = self.client.get(reverse("catalog:product_detail", kwargs={"slug": self.laptop.slug}))
        self.assertEqual(response.status_code, 200)
        related = list(response.context["related_products"])
        self.assertIn(laptop2, related)
        self.assertNotIn(self.laptop, related)          # Must exclude self
        self.assertNotIn(self.inactive_item, related)   # Must exclude inactive
        self.assertNotIn(self.audio, related)           # Must exclude other categories

    def test_categories_context_processor(self):
        """Global context processor supplies active categories ordered by order."""
        request = RequestFactory().get("/")
        data = category_navigation(request)
        self.assertIn("nav_categories", data)
        cats = list(data["nav_categories"])
        self.assertIn(self.cat_laptops, cats)
        self.assertIn(self.cat_audio, cats)


class CatalogAdminAndVisibilityTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="catalogadmin",
            email="admin@novastore.local",
            password="AdminPassword123!",
        )
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
            b"\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00"
            b"\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
        )
        self.test_img = SimpleUploadedFile("test_cat.gif", small_gif, content_type="image/gif")
        self.category = Category.objects.create(name="Tablets", slug="tablets", order=1, is_active=True)

    def test_catalog_admin_access_for_staff(self):
        """Staff/superusers can access Product and Category changelists in Admin."""
        self.client.login(username="catalogadmin", password="AdminPassword123!")
        cat_resp = self.client.get("/admin/catalog/category/")
        self.assertEqual(cat_resp.status_code, 200)
        self.assertContains(cat_resp, "Tablets")

        prod_resp = self.client.get("/admin/catalog/product/")
        self.assertEqual(prod_resp.status_code, 200)

    def test_active_inactive_full_visibility_lifecycle(self):
        """
        Verify end-to-end visibility lifecycle:
        1. When active: appears in catalog, search, and detail page loads HTTP 200.
        2. When toggled to inactive: immediately disappears from catalog and search, detail returns HTTP 404.
        3. When reactivated: immediately reappears on all public views.
        """
        product = Product.objects.create(
            category=self.category,
            name="NovaPad Ultra Experimental",
            slug="novapad-ultra-experimental",
            tagline="Next-gen display",
            description="Quantum dot OLED tablet with M3 chip.",
            price=Decimal("89900.00"),
            image=self.test_img,
            is_active=True,
        )

        # 1. Active State
        catalog_res = self.client.get(reverse("catalog:product_list"))
        self.assertContains(catalog_res, "NovaPad Ultra Experimental")
        search_res = self.client.get(reverse("catalog:product_list") + "?q=Quantum")
        self.assertContains(search_res, "NovaPad Ultra Experimental")
        detail_res = self.client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))
        self.assertEqual(detail_res.status_code, 200)

        # 2. Inactivate
        product.is_active = False
        product.save()

        catalog_res2 = self.client.get(reverse("catalog:product_list"))
        self.assertNotContains(catalog_res2, "NovaPad Ultra Experimental")
        search_res2 = self.client.get(reverse("catalog:product_list") + "?q=Quantum")
        self.assertNotContains(search_res2, "NovaPad Ultra Experimental")
        detail_res2 = self.client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))
        self.assertEqual(detail_res2.status_code, 404)

        # 3. Reactivate
        product.is_active = True
        product.save()

        catalog_res3 = self.client.get(reverse("catalog:product_list"))
        self.assertContains(catalog_res3, "NovaPad Ultra Experimental")
        detail_res3 = self.client.get(reverse("catalog:product_detail", kwargs={"slug": product.slug}))
        self.assertEqual(detail_res3.status_code, 200)
