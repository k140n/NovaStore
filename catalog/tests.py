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
        # Create a tiny 1x1 transparent PNG for image testing
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
        # 134900 -> ₹1,34,900
        self.assertEqual(self.product.formatted_price, "₹1,34,900")
        self.assertEqual(self.product.formatted_original_price, "₹1,44,900")

    def test_discount_calculation(self):
        # (144900 - 134900) / 144900 = 10000 / 144900 ~= 6.9% -> 7%
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
