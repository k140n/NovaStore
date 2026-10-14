from decimal import Decimal
import io
import os
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont
from catalog.models import Category, Product, ProductSpecification
from core.models import Banner


def create_mock_image(width, height, text, bg_color=(24, 24, 27), text_color=(245, 245, 247), subtitle="NovaStore"):
    """
    Generate an elegant, minimal Apple-style product mockup image using Pillow.
    """
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Subtle inner gradient / vignette effect
    for i in range(min(width, height) // 8):
        alpha = int(255 * (1 - i / (min(width, height) // 8)))
        # Draw soft outer frame
        border_col = (
            min(255, bg_color[0] + 10),
            min(255, bg_color[1] + 10),
            min(255, bg_color[2] + 12),
        )

    # Draw centered decorative card
    card_inset_x = int(width * 0.1)
    card_inset_y = int(height * 0.1)
    draw.rounded_rectangle(
        [(card_inset_x, card_inset_y), (width - card_inset_x, height - card_inset_y)],
        radius=20,
        outline=(60, 60, 67),
        width=2,
    )

    # Draw simple title text
    # Fallback to default bitmap font if TTF not available
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # Draw title and subtitle
    draw.text((width // 2, height // 2 - 20), text, fill=text_color, anchor="mm", font=font)
    draw.text((width // 2, height // 2 + 20), subtitle, fill=(134, 134, 139), anchor="mm", font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()


from pathlib import Path
from django.conf import settings

SEED_IMAGE_DIR = settings.BASE_DIR / "static" / "images" / "seed"


def get_image_data_or_mock(seed_filename, width, height, text, bg_color, subtitle="NovaStore"):
    """
    Attempt to load high-res photography from static/images/seed.
    Fallback to elegant Pillow generated mockup if file not found.
    """
    seed_path = SEED_IMAGE_DIR / seed_filename
    if seed_path.exists():
        with open(seed_path, "rb") as f:
            return f.read()
    return create_mock_image(width, height, text, bg_color=bg_color, subtitle=subtitle)


def file_is_missing_on_disk(image_field):
    """
    Check if the FileField has no file attached OR the physical file is missing from disk.
    """
    if not image_field or not image_field.name:
        return True
    try:
        return not image_field.storage.exists(image_field.name)
    except Exception:
        return True


class Command(BaseCommand):
    help = "Seeds database with initial categories, products, specifications, and banners."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding NovaStore data..."))

        # 1. Banners
        banners_data = [
            {
                "title": "NovaPhone 16 Pro",
                "subtitle": "Titanium. So strong. So light. So Pro.",
                "description": "Engineered with Grade 5 titanium, the revolutionary A18 Pro chip, and unprecedented camera intelligence.",
                "badge_text": "Flagship Release",
                "button_text": "Buy NovaPhone 16 Pro",
                "button_link": "/catalog/smartphones/",
                "order": 1,
                "color": (15, 23, 42),
            },
            {
                "title": "NovaBook Pro 16",
                "subtitle": "Mind-blowing. Head-turning. Extreme performance.",
                "description": "Featuring NovaSilicon M3 Max, up to 128GB unified memory, and 22 hours of battery life.",
                "badge_text": "Pro Performance",
                "button_text": "Explore NovaBook Pro",
                "button_link": "/catalog/laptops/",
                "order": 2,
                "color": (24, 24, 27),
            },
            {
                "title": "NovaPods Max",
                "subtitle": "Symphonic sound. Total silence.",
                "description": "Active Noise Cancellation, Personalized Spatial Audio, and lossless listening via USB-C.",
                "badge_text": "Audiophile Choice",
                "button_text": "Discover Audio",
                "button_link": "/catalog/audio/",
                "order": 3,
                "color": (30, 27, 75),
            },
        ]

        for idx, b in enumerate(banners_data, start=1):
            color = b.pop("color")
            banner, created = Banner.objects.get_or_create(
                title=b["title"],
                defaults={**b},
            )
            seed_file = f"banner_{idx}.jpg"
            if created or file_is_missing_on_disk(banner.image):
                img_data = get_image_data_or_mock(seed_file, 1600, 700, b["title"], bg_color=color, subtitle=b["subtitle"])
                banner.image.save(f"banner_{banner.id}.jpg", ContentFile(img_data), save=True)
            self.stdout.write(f"  ✓ Banner: {banner.title}")

        # 2. Categories
        categories_data = [
            {"name": "Laptops", "slug": "laptops", "order": 1, "desc": "Powerful notebooks for creators and professionals."},
            {"name": "Smartphones", "slug": "smartphones", "order": 2, "desc": "Flagship mobile computing with next-gen camera systems."},
            {"name": "Tablets", "slug": "tablets", "order": 3, "desc": "Ultra-versatile digital canvas and portable workstations."},
            {"name": "Audio", "slug": "audio", "order": 4, "desc": "Immersive acoustics, noise cancellation, and high fidelity."},
            {"name": "Accessories", "slug": "accessories", "order": 5, "desc": "Precision chargers, keyboards, displays, and cases."},
        ]

        category_map = {}
        for c in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=c["slug"],
                defaults={"name": c["name"], "description": c["desc"], "order": c["order"], "is_active": True},
            )
            seed_file = f"cat_{cat.slug}.jpg"
            if created or file_is_missing_on_disk(cat.image):
                img_data = get_image_data_or_mock(seed_file, 600, 400, cat.name, bg_color=(20, 20, 23), subtitle="NovaStore Category")
                cat.image.save(f"cat_{cat.slug}.jpg", ContentFile(img_data), save=True)
            category_map[c["slug"]] = cat
            self.stdout.write(f"  ✓ Category: {cat.name}")

        # 3. Products
        products_data = [
            # Laptops
            {
                "category": category_map["laptops"],
                "name": "NovaBook Pro 16",
                "slug": "novabook-pro-16",
                "tagline": "Extreme power for extreme workflows.",
                "description": "NovaBook Pro 16 blasts forward with the M3 Max chip. Up to 16-core CPU, 40-core GPU, Liquid Retina XDR display, and 128GB unified memory.",
                "price": Decimal("249900.00"),
                "original_price": Decimal("269900.00"),
                "is_featured": True,
                "stock": 18,
                "specs": [
                    ("Processor", "NovaSilicon M3 Max (16-Core CPU, 40-Core GPU)"),
                    ("Display", "16.2-inch Liquid Retina XDR (3456x2234, 120Hz ProMotion)"),
                    ("Memory", "36GB Unified Memory (Configurable to 128GB)"),
                    ("Storage", "1TB Superfast NVMe SSD"),
                    ("Battery", "Up to 22 hours video playback (100Wh)"),
                ],
            },
            {
                "category": category_map["laptops"],
                "name": "NovaBook Air 15",
                "slug": "novabook-air-15",
                "tagline": "Lean. Mean. M3 machine.",
                "description": "Impossibly thin and fast. NovaBook Air with M3 makes working and gaming effortless with a striking 15.3-inch Liquid Retina display.",
                "price": Decimal("134900.00"),
                "original_price": Decimal("144900.00"),
                "is_featured": True,
                "stock": 25,
                "specs": [
                    ("Processor", "NovaSilicon M3 (8-Core CPU, 10-Core GPU)"),
                    ("Display", "15.3-inch Liquid Retina (2880x1864, 500 nits)"),
                    ("Memory", "16GB Unified Memory"),
                    ("Storage", "512GB SSD"),
                    ("Weight", "1.51 kg lightweight aluminum unibody"),
                ],
            },
            {
                "category": category_map["laptops"],
                "name": "NovaBook Pro 14",
                "slug": "novabook-pro-14",
                "tagline": "Pro in every dimension.",
                "description": "Compact powerhouse. Delivers uncompromised sustained performance with whisper-quiet active cooling and studio-quality mics.",
                "price": Decimal("199900.00"),
                "original_price": Decimal("209900.00"),
                "is_featured": False,
                "stock": 14,
                "specs": [
                    ("Processor", "NovaSilicon M3 Pro (12-Core CPU, 18-Core GPU)"),
                    ("Display", "14.2-inch Liquid Retina XDR (3024x1964, 1600 nits peak)"),
                    ("Memory", "18GB Unified Memory"),
                    ("Storage", "512GB SSD"),
                    ("Ports", "3x Thunderbolt 4, HDMI, SDXC, MagSafe 3"),
                ],
            },

            # Smartphones
            {
                "category": category_map["smartphones"],
                "name": "NovaPhone 16 Pro Max",
                "slug": "novaphone-16-pro-max",
                "tagline": "Titanium. Camera Control. 4K 120 fps Dolby Vision.",
                "description": "The ultimate smartphone experience. Featuring Grade 5 titanium, thinnest borders ever, and revolutionary Camera Control button.",
                "price": Decimal("144900.00"),
                "original_price": Decimal("154900.00"),
                "is_featured": True,
                "stock": 30,
                "specs": [
                    ("Processor", "Nova A18 Pro chip with 6-core GPU & Neural Engine"),
                    ("Display", "6.9-inch Super Retina XDR OLED with Always-On"),
                    ("Camera", "48MP Fusion + 48MP Ultra Wide + 12MP 5x Telephoto"),
                    ("Material", "Aerospace-grade Titanium with textured matte glass"),
                    ("Battery", "Up to 33 hours video playback"),
                ],
            },
            {
                "category": category_map["smartphones"],
                "name": "NovaPhone 16",
                "slug": "novaphone-16",
                "tagline": "Hello, Intelligence. Bold color infused.",
                "description": "Powerful 48MP Fusion 2-in-1 camera, Action button, Camera Control, and durable color-infused back glass.",
                "price": Decimal("79900.00"),
                "original_price": Decimal("89900.00"),
                "is_featured": True,
                "stock": 40,
                "specs": [
                    ("Processor", "Nova A18 chip with 5-core GPU"),
                    ("Display", "6.1-inch Super Retina XDR OLED"),
                    ("Camera", "48MP Fusion main with 2x optical-quality telephoto"),
                    ("Durability", "Ceramic Shield front, tougher than any smartphone glass"),
                    ("Charging", "USB-C with fast MagSafe wireless charging"),
                ],
            },

            # Tablets
            {
                "category": category_map["tablets"],
                "name": "NovaPad Pro 13",
                "slug": "novapad-pro-13",
                "tagline": "Thinpossible. Breakthrough Ultra Retina Tandem OLED.",
                "description": "The thinnest device we've ever created. Outrageously powerful M4 chip, Ultra Retina XDR display, and Nova Pencil Pro support.",
                "price": Decimal("129900.00"),
                "original_price": Decimal("139900.00"),
                "is_featured": True,
                "stock": 12,
                "specs": [
                    ("Processor", "NovaSilicon M4 chip with Hardware Ray Tracing"),
                    ("Display", "13-inch Ultra Retina Tandem OLED (1600 nits peak)"),
                    ("Thickness", "Unbelievable 5.1 mm ultra-thin design"),
                    ("Audio", "Four-speaker sound system with studio-quality mics"),
                    ("Connectivity", "Thunderbolt / USB 4 & Wi-Fi 6E"),
                ],
            },
            {
                "category": category_map["tablets"],
                "name": "NovaPad Air 11",
                "slug": "novapad-air-11",
                "tagline": "Fresh Air. Serious power.",
                "description": "Powered by the versatile M2 chip. Gorgeous Liquid Retina display, landscape front camera, and blazing-fast connectivity.",
                "price": Decimal("59900.00"),
                "original_price": None,
                "is_featured": False,
                "stock": 20,
                "specs": [
                    ("Processor", "NovaSilicon M2 chip"),
                    ("Display", "11-inch Liquid Retina with True Tone and P3 wide color"),
                    ("Camera", "Landscape 12MP Center Stage Ultra Wide"),
                    ("Storage", "128GB high-speed flash"),
                ],
            },

            # Audio
            {
                "category": category_map["audio"],
                "name": "NovaPods Max",
                "slug": "novapods-max",
                "tagline": "An over-ear symphony. Pure high-fidelity audio.",
                "description": "Custom acoustic design, H1 computational audio, personalized spatial audio with dynamic head tracking, and USB-C.",
                "price": Decimal("59900.00"),
                "original_price": Decimal("64900.00"),
                "is_featured": True,
                "stock": 15,
                "specs": [
                    ("Acoustics", "Nova-designed 40mm dynamic driver"),
                    ("Noise Cancellation", "Pro-level Active Noise Cancellation with Transparency mode"),
                    ("Battery", "20 hours listening with ANC and Spatial Audio enabled"),
                    ("Weight", "384.8 g with breathable knit mesh canopy"),
                ],
            },
            {
                "category": category_map["audio"],
                "name": "NovaPods Pro 2",
                "slug": "novapods-pro-2",
                "tagline": "Adaptive Audio. Up to 2x more Active Noise Cancellation.",
                "description": "Next-level H2 chip powers Adaptive Audio, Transparency mode, Conversation Awareness, and MagSafe USB-C charging case.",
                "price": Decimal("24900.00"),
                "original_price": None,
                "is_featured": True,
                "stock": 50,
                "specs": [
                    ("Chip", "Nova H2 headphone chip & U1 chip in case"),
                    ("Water Resistance", "IP54 dust, sweat, and water resistant"),
                    ("Battery", "Up to 6 hours listening (30 hours with case)"),
                ],
            },

            # Accessories
            {
                "category": category_map["accessories"],
                "name": "Nova Studio Display 27",
                "slug": "nova-studio-display-27",
                "tagline": "A sight to be bold. 5K Retina masterpiece.",
                "description": "27-inch 5K Retina display, 12MP Ultra Wide camera with Center Stage, studio-quality three-mic array, and six-speaker sound.",
                "price": Decimal("159900.00"),
                "original_price": Decimal("169900.00"),
                "is_featured": False,
                "stock": 8,
                "specs": [
                    ("Resolution", "5120x2880 at 218 ppi, 600 nits brightness"),
                    ("Camera", "12MP Ultra Wide camera with 122° field of view"),
                    ("Audio", "High-fidelity six-speaker system with force-cancelling woofers"),
                    ("Ports", "1x Thunderbolt 3 upstream, 3x USB-C downstream"),
                ],
            },
        ]

        for p in products_data:
            specs = p.pop("specs")
            product, created = Product.objects.get_or_create(
                slug=p["slug"],
                defaults={**p},
            )
            seed_file = f"prod_{product.slug}.jpg"
            if created or file_is_missing_on_disk(product.image):
                img_data = get_image_data_or_mock(seed_file, 800, 800, product.name, bg_color=(25, 25, 28), subtitle=product.category.name)
                product.image.save(f"prod_{product.slug}.jpg", ContentFile(img_data), save=True)

            # Sync specifications
            ProductSpecification.objects.filter(product=product).delete()
            for idx, (s_name, s_val) in enumerate(specs, start=1):
                ProductSpecification.objects.create(
                    product=product,
                    name=s_name,
                    value=s_val,
                    order=idx,
                )
            self.stdout.write(f"  ✓ Product: {product.name} ({len(specs)} specs)")

        # 4. Demo Accounts
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@novastore.local", "adminpassword123")
            self.stdout.write("  ✓ Superuser created: admin / adminpassword123")
        else:
            self.stdout.write("  ✓ Superuser exists: admin")

        if not User.objects.filter(username="customer").exists():
            User.objects.create_user("customer", "customer@novastore.local", "customerpassword123", first_name="Alex", last_name="Rivera")
            self.stdout.write("  ✓ Customer demo account created: customer / customerpassword123")
        else:
            self.stdout.write("  ✓ Customer demo account exists: customer")

        self.stdout.write(self.style.SUCCESS("NovaStore demonstration data seeded successfully!"))
