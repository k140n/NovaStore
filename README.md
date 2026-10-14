# NovaStore — Premium Electronics E-Commerce

NovaStore is an original, responsive electronics e-commerce web application inspired by the clean, minimalist shopping experience of modern digital storefronts (such as Apple India). Built with **Python 3.12**, **Django 5.2 LTS**, vanilla CSS3, and modern standards.

---

## Features & Milestones Roadmap

- [x] **Milestone 1**: Project initialization, environment setup, 12-factor configuration, core routing, automated tests.
- [x] **Milestone 2**: Category, Product, and Banner models, migrations, media upload handling, Django Admin integration with image previews.
- [x] **Milestone 3**: Apple-inspired layout, responsive navigation, dynamic banners, featured products showcase, promotional sections.
- [x] **Milestone 4**: Product catalogue, category filtering, search, detail view, specifications grid, 404/empty states.
- [x] **Milestone 5**: User authentication (register, login, logout, account profile) with Django's secure auth system.
- [x] **Milestone 6**: Comprehensive automated test suite (models, views, filters, auth, visibility rules).
- [x] **Milestone 7**: Security audit, accessibility (a11y), responsive design polishing across mobile, tablet, and desktop.
- [x] **Milestone 8**: Production readiness (Gunicorn, WhiteNoise, PostgreSQL support, render deployment config).
- [x] **Milestone 9**: Deployment verification, admin seeding, submission checklist.

---

## Tech Stack

- **Backend**: Python 3.12, Django 5.2 LTS
- **Database**: SQLite (Local Development) / PostgreSQL (Production via `dj-database-url`)
- **WSGI Server**: Gunicorn 25.1+
- **Static & Media Asset Handling**: WhiteNoise 6.12+ (Brotli/Gzip compression), Pillow 12.3+
- **Frontend**: Django Templates, Semantic HTML5, Vanilla CSS3 (Custom Apple-Caliber Design System), Vanilla JS
- **Security & a11y**: WCAG 2.1 AA compliant, strict Clickjacking (`X-Frame-Options: DENY`), MIME sniffing protection (`nosniff`), SameSite cookie policy, automated test suite (74 tests)

---

## Project Structure

```text
NovaStore/
├── .env.example            # Sanitized environment variables template
├── .gitignore              # Python/Django/OS ignore rules
├── README.md               # Architecture, setup & deployment documentation
├── requirements.txt        # Pinned project dependencies
├── Procfile                # PaaS web process configuration (Gunicorn WSGI)
├── build.sh                # Executable PaaS build script (Render/Railway)
├── render.yaml             # 1-click Render Blueprint definition (Web + PostgreSQL)
├── manage.py               # Django management utility
├── config/                 # Root configuration package
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # 12-factor settings (dotenv, whitenoise, dj-database-url)
│   ├── urls.py             # Root URL routing, error previews, media handling
│   └── wsgi.py
├── core/                   # Shared layouts, homepage, banners
│   ├── admin.py            # Custom banner admin with image previews
│   ├── apps.py
│   ├── models.py           # Banner model with active filtering and ordering
│   ├── tests.py            # Homepage, banner, admin CRUD, security, and a11y tests
│   ├── urls.py
│   └── views.py
├── catalog/                # Categories, products, specifications
│   ├── admin.py            # Category and Product admin with TabularInlines
│   ├── apps.py
│   ├── context_processors.py # Global active categories navigation provider
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py # Automated database seeding with realistic hardware
│   ├── models.py           # Category, Product, ProductSpecification models
│   ├── tests.py            # 35 unit/integration tests for catalog and filters
│   ├── urls.py
│   └── views.py            # Product list, filters, search, sorting, detail view
├── accounts/               # Authentication & user profiles
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py            # Registration, login, profile, and password forms
│   ├── tests.py            # 21 unit/integration tests for authentication flows
│   ├── urls.py
│   └── views.py            # Register, login, logout, profile dashboard, password change
├── static/                 # Static assets
│   ├── css/style.css       # Design system tokens, components, responsive breakpoints
│   └── js/main.js          # Carousel, search dropdown, mobile drawer, toasts
├── templates/              # HTML Templates
│   ├── base.html           # Master layout with skip-link, nav, and footer
│   ├── 404.html            # Apple-style custom 404 error page
│   ├── 500.html            # Apple-style custom 500 error page
│   ├── core/
│   ├── catalog/
│   └── accounts/
└── media/                  # User uploads (product images, banners)
```

---

## Local Setup & Development

### 1. Prerequisites
- Python 3.12+
- Git
- Virtualenv (`python3 -m venv`)

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone <repository_url>
cd NovaStore

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
cp .env.example .env
```
Default `.env` configuration works out of the box with SQLite for local development.

### 4. Database Migrations
```bash
python manage.py migrate
```

### 5. Seed Demonstration Data
Populate the store with realistic electronics hardware, banners, and technical specifications:
```bash
python manage.py seed_data
```

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
# Default local admin credentials:
# Username: admin
# Password: adminpassword123
```

### 7. Run Automated Tests
```bash
python manage.py test
```
All 74 tests should pass with `OK` (0 failures, 0 errors).

### 8. Run the Development Server
```bash
python manage.py runserver 127.0.0.1:8080
```
Visit the store at `http://127.0.0.1:8080/` and the admin portal at `http://127.0.0.1:8080/admin/`.

---

## Production Deployment Guide

NovaStore is engineered as a **12-factor cloud-ready application** ready for automated deployment on **Render**, **Railway**, or **Heroku**.

### Deploying on Render (Recommended)

1. **Option A: 1-Click Blueprint (Using `render.yaml`)**:
   - Link your GitHub repository in the [Render Dashboard](https://dashboard.render.com).
   - Select **Blueprints** and choose your repository.
   - Render automatically provisions:
     - A Python Web Service running Gunicorn.
     - A managed PostgreSQL database.
     - Automatically generates `SECRET_KEY` and links `DATABASE_URL`.

2. **Option B: Manual Web Service Setup**:
   - Create a new **Web Service** on Render connected to your repository.
   - Set the following settings:
     - **Runtime**: `Python 3`
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --threads 2`
   - Add a managed **PostgreSQL Database** on Render and copy its Internal Database URL into the web service's `DATABASE_URL` environment variable.

### Production Environment Variables Reference

| Variable | Description | Example / Recommended Value |
|---|---|---|
| `SECRET_KEY` | Cryptographic secret for signing sessions and tokens | Random 50+ character string |
| `DEBUG` | Enables/disables debug mode and tracebacks | `False` |
| `ALLOWED_HOSTS` | Permitted HTTP host headers (comma-separated) | `novastore.onrender.com,.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins for HTTPS POST requests | `https://*.onrender.com,https://yourdomain.com` |
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://user:pass@host:5432/dbname` |
| `SECURE_SSL_REDIRECT` | Automatically redirect all HTTP traffic to HTTPS | `True` |
| `SECURE_HSTS_SECONDS` | HTTP Strict Transport Security duration | `31536000` (1 year) |

---

## Static & Media File Architecture

- **Static Assets** (`/static/`):
  Collected into `STATIC_ROOT` (`staticfiles/`) using WhiteNoise via `python manage.py collectstatic --noinput`.
  WhiteNoise provides high-performance compression (Gzip/Brotli) and cache-control headers (`max-age=31536000, immutable`).
- **Media Uploads** (`/media/`):
  Handled via Django's `FileSystemStorage` locally and served via Django URL patterns during development. In containerized production, persistent volumes or S3-compatible cloud storage can be mounted to `MEDIA_ROOT`.

---

## Security & Compliance Highlights

- **Clickjacking Defense**: `X-Frame-Options = 'DENY'` header enforced across all responses.
- **MIME Sniffing Defense**: `X-Content-Type-Options = 'nosniff'` enforced.
- **Session Protection**: `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`.
- **CSRF Defense**: All state-changing POST endpoints protected with `CsrfViewMiddleware` and `{% csrf_token %}`.
- **Accessibility (WCAG 2.1 AA)**: Keyboard skip-to-content link, high-contrast `:focus-visible` focus rings, single `<h1>` hierarchy, ARIA navigation labels, and `@media (prefers-reduced-motion: reduce)` support.

