# NovaStore — Premium Electronics E-Commerce

NovaStore is an original, responsive electronics e-commerce web application inspired by the clean, minimalist shopping experience of modern digital storefronts (such as Apple India). Built with **Python 3.12**, **Django 5.2 LTS**, vanilla CSS3, and modern standards.

---

## Features & Milestones Roadmap

- [x] **Milestone 1**: Project initialization, environment setup, 12-factor configuration, core routing, automated tests.
- [x] **Milestone 2**: Category, Product, and Banner models, migrations, media upload handling, Django Admin integration with image previews.
- [x] **Milestone 3**: Apple-inspired layout, responsive navigation, dynamic banners, featured products showcase, promotional sections.
- [x] **Milestone 4**: Product catalogue, category filtering, search, detail view, specifications grid, 404/empty states.
- [x] **Milestone 5**: User authentication (register, login, logout, account profile) with Django's secure auth system.
- [ ] **Milestone 6**: Comprehensive automated test suite (models, views, filters, auth, visibility rules).
- [ ] **Milestone 7**: Security audit, accessibility (a11y), responsive design polishing across mobile, tablet, and desktop.
- [ ] **Milestone 8**: Production readiness (Gunicorn, WhiteNoise, PostgreSQL support, render deployment config).
- [ ] **Milestone 9**: Deployment verification, admin seeding, submission checklist.

---

## Tech Stack

- **Backend**: Python 3.12, Django 5.2 LTS
- **Database**: SQLite (Local Development) / PostgreSQL (Production)
- **Frontend**: Django Templates, HTML5, Vanilla CSS3 (Custom Design System), Vanilla JS
- **Media & Assets**: Pillow, WhiteNoise
- **Deployment**: Gunicorn, WhiteNoise, Render / PaaS

---

## Project Structure

```text
NovaStore/
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules for Python/Django
├── README.md               # Documentation & setup guide
├── requirements.txt        # Pinned project dependencies
├── manage.py               # Django management utility
├── config/                 # Root configuration package
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # 12-factor settings (dotenv, whitenoise, dj-database-url)
│   ├── urls.py             # Root URL routing & media handling
│   └── wsgi.py
├── core/                   # Shared layouts, homepage, banners
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── catalog/                # Categories, products, specifications
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── accounts/               # Authentication & user profiles
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── static/                 # Static assets
│   ├── css/style.css       # Custom design system
│   ├── js/main.js          # Client-side scripts
│   └── images/
├── templates/              # HTML Templates
│   ├── base.html           # Master layout with responsive nav & footer
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
Edit `.env` if needed (default values work out-of-the-box for local development).

### 4. Database Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser (Admin)
```bash
python manage.py createsuperuser
# Or default local admin:
# Username: admin
# Password: adminpassword123
```

### 6. Run Automated Tests
```bash
python manage.py test
```

### 7. Run the Development Server
```bash
python manage.py runserver
```
Visit the store at `http://127.0.0.1:8000/` and the admin portal at `http://127.0.0.1:8000/admin/`.
