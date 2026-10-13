# Household Inventory Manager

A server-rendered Django application for keeping track of what you own and where it is stored. Items are organised by location (Kitchen, Garage, Office, ...). Every page is plain HTML rendered on the server: **no JavaScript framework, no client-side build step**.

The project demonstrates four things:

1. **Django MVT** with generic class-based views and a ForeignKey relationship.
2. **Template inheritance** (`base.html` with `content` and `styles` blocks).
3. **A scalable CSS architecture** (`base/`, `components/`, `pages/`) where page-specific styles load only on the pages that need them.
4. **Production-ready static files** (`STATIC_ROOT` and `collectstatic`) and **accessible forms** (labels, visible focus, linked error messages).

---

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
- [Running the Application](#running-the-application)
- [Static Files](#static-files)
- [Running the tests](#running-the-tests)
- [URL reference](#url-reference)
- [Project structure](#project-structure)
- [Data model](#data-model)
- [Template inheritance](#template-inheritance)
- [CSS architecture](#css-architecture)
- [Accessibility](#accessibility)
- [Configuration](#configuration)
- [Deploying to production](#deploying-to-production)
- [Troubleshooting](#troubleshooting)

---

## Features

- Full **CRUD for locations** and **CRUD for items** (list, add, edit, delete).
- Delete **confirmation pages** (GET shows the page, POST deletes). Deleting a location warns how many items will be deleted with it.
- **Search and filter** the item list by name, description, and location.
- **Validation errors next to each field**, with a summary above the form.
- **Flash messages** after every successful action.
- Friendly **empty states** that tell you what to do next.
- Responsive layout: tables turn into stacked rows on small screens.
- Django admin registered for both models.

## Requirements

- Python 3.10 or newer
- pip
- No other system dependencies. The only Python dependency is Django (see `requirements.txt`). The database is SQLite.

## Setup

Run these commands from the repository root (the folder containing `manage.py`).

**1. Create and activate a virtual environment**

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

```powershell
# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
```

**2. Install dependencies from `requirements.txt`**

```bash
pip install -r requirements.txt
```

**3. Check the project**

```bash
python manage.py check
```

You should see `System check identified no issues (0 silenced).`

No `.env` file is needed for local development. Sensible defaults are built in (see [Configuration](#configuration)).

## Running the Application

**1. Run database migrations** (creates `db.sqlite3` with the `Location` and `Item` tables):

```bash
python manage.py migrate
```

**2. Start the development server:**

```bash
python manage.py runserver
```

**3. Open the app** at <http://127.0.0.1:8000/>. The home page redirects to the item list.

A good first walk-through:

1. Open **Locations** and choose **Add location**. Create "Kitchen".
2. Choose **Add item here** next to Kitchen, or use **Items → Add item**, and create an item.
3. Go back to **Items** and try the search box and the location filter.
4. Edit and delete the item. Delete the location to see the confirmation warning.

Optional: create an admin user to use `/admin/`:

```bash
python manage.py createsuperuser
```

## Static Files

Static files (CSS here) are handled differently in development and production.

**Development (`DEBUG=True`)**: nothing to do. `runserver` finds files in `inventory/static/` automatically.

**Production (`DEBUG=False`)**: Django does not serve static files. Collect them into one directory and let your web server (Nginx, Apache, a CDN) serve that directory:

```bash
python manage.py collectstatic
```

This copies every stylesheet into `STATIC_ROOT`, which is configured in `config/settings.py`:

```python
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
```

After running it you will find a `staticfiles/` directory containing `css/base/`, `css/components/`, `css/pages/` and the admin's assets. Use `python manage.py collectstatic --noinput` in scripts and CI. The directory is generated output, so it is git-ignored. Never edit files inside it, and re-run the command after every CSS change you deploy.

> `STATICFILES_DIRS` is not used because all assets live inside the `inventory` app's `static/` directory. `STATIC_ROOT` is only the *destination* for `collectstatic`.

## Running the tests

```bash
python manage.py test
```

The suite (66 tests) covers the models, every endpoint's GET and POST behaviour (including invalid input and 404s), template inheritance, the CSS directory structure, page-specific stylesheet loading, the focus-indicator rule, `STATIC_ROOT`, and this README's required content.

## URL reference

| Method | URL | Purpose |
| --- | --- | --- |
| GET | `/` | Redirects to `/items/` |
| GET | `/locations/` | List all locations (with item counts) |
| GET / POST | `/locations/add/` | Show the form / create a location |
| GET / POST | `/locations/<pk>/edit/` | Show the form / update a location |
| GET / POST | `/locations/<pk>/delete/` | Show confirmation / delete a location |
| GET | `/items/` | List all items. Optional `?q=text` and `?location=<pk>` filters |
| GET / POST | `/items/add/` | Show the form / create an item. Optional `?location=<pk>` preselects a location |
| GET / POST | `/items/<pk>/edit/` | Show the form / update an item |
| GET / POST | `/items/<pk>/delete/` | Show confirmation / delete an item |
| GET | `/admin/` | Django admin |

Invalid POSTs re-render the form with status `200` and the errors; valid POSTs redirect (`302`) to the list page.

## Project structure

```
household_inventory_manager/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── config/                      # Project package
│   ├── settings.py              # Settings, including STATIC_URL / STATIC_ROOT
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── templates/                   # Project-level templates
│   ├── base.html                # Master layout (blocks: title, styles, content)
│   ├── 404.html
│   └── 500.html
└── inventory/                   # The app
    ├── models.py                # Location, Item
    ├── forms.py                 # LocationForm, ItemForm (ModelForms)
    ├── views.py                 # Class-based views
    ├── urls.py
    ├── admin.py
    ├── migrations/
    ├── templates/inventory/
    │   ├── item_list.html
    │   ├── item_form.html
    │   ├── item_confirm_delete.html
    │   ├── location_list.html
    │   ├── location_form.html
    │   ├── location_confirm_delete.html
    │   └── partials/
    │       ├── _form_field.html     # One field: label, help, input, errors
    │       └── _form_errors.html    # Error summary above a form
    ├── static/css/
    │   ├── base/                    # Global: tokens, reset, typography, layout
    │   │   ├── main.css
    │   │   └── layout.css
    │   ├── components/              # Reusable UI pieces
    │   │   ├── buttons.css
    │   │   ├── forms.css
    │   │   ├── messages.css
    │   │   └── table.css
    │   └── pages/                   # One file per page that needs its own styles
    │       ├── item_list.css
    │       ├── location_list.css
    │       ├── form_page.css
    │       └── confirm_delete.css
    └── tests/
```

## Data model

```
Location 1 ────< Item
```

| Model | Field | Type | Options |
| --- | --- | --- | --- |
| `Location` | `name` | `CharField` | `max_length=100`, `unique=True` |
| `Item` | `name` | `CharField` | `max_length=100` |
| `Item` | `description` | `TextField` | `blank=True` |
| `Item` | `quantity` | `IntegerField` | `default=1` |
| `Item` | `location` | `ForeignKey(Location)` | `on_delete=models.CASCADE` |

Because of `CASCADE`, deleting a location deletes its items. The delete confirmation page says so explicitly.

Validation beyond the field options lives in the forms: names are trimmed and must not be blank, location names are unique ignoring case ("kitchen" and "Kitchen" collide), and quantity cannot be negative.

## Template inheritance

`templates/base.html` holds the whole page skeleton (`<html>`, `<head>`, `<body>`, header, navigation, message area, footer) and defines three blocks:

| Block | Location | Used for |
| --- | --- | --- |
| `{% block title %}` | `<title>` | Page title |
| `{% block styles %}` | inside `<head>` | Page-specific stylesheets |
| `{% block content %}` | inside `<main>` | Page content |

Every page template starts with `{% extends 'base.html' %}` and fills these blocks. Form markup that repeats is extracted into two partials with `{% include %}`.

## CSS architecture

Stylesheets are split by how widely they are used:

| Directory | Loaded | Contents |
| --- | --- | --- |
| `css/base/` | Every page (from `base.html`) | Design tokens (CSS variables), reset, typography, page shell |
| `css/components/` | Buttons, forms and messages on every page. `table.css` only on pages with a table | Reusable pieces: `.btn`, form fields, status messages, data tables |
| `css/pages/` | Only on the page that needs it, through `{% block styles %}` | Styles for one page or page type |

For example, `item_list.html` adds its own stylesheet like this:

```django
{% block styles %}
    <link rel="stylesheet" href="{% static 'css/components/table.css' %}">
    <link rel="stylesheet" href="{% static 'css/pages/item_list.css' %}">
{% endblock %}
```

so `/locations/` never downloads `item_list.css`. Colours, spacing and fonts are defined once as CSS variables in `base/main.css`. Changing a variable restyles the whole app.

## Accessibility

- Every input has a `<label>` connected with `for`/`id`.
- Visible **focus indicator** on `input`, `textarea`, and `select` (both `:focus` and `:focus-visible`) with a 3px blue outline and an offset, defined in `components/forms.css`. Links and buttons get the same treatment. Outlines are never removed.
- Validation errors render as `<ul class="errorlist">` directly under the field. Django links them to the input with `aria-describedby` and sets `aria-invalid="true"`. Errors are also styled distinctly (red text, red field border, and the word "Error:"), so colour is not the only signal.
- A skip link, a landmark structure (`header`, `nav`, `main`, `footer`), `aria-current` on the active navigation link, and visually hidden text that gives "Edit" and "Delete" links the name of the item they act on.
- Status messages use `role="status"` so screen readers announce them.
- Animations are disabled for users who prefer reduced motion.

## Configuration

Settings are read from environment variables, all optional for local work:

| Variable | Default | Meaning |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | An insecure development key | **Set this in production** |
| `DJANGO_DEBUG` | `True` | Set to `False` in production |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,[::1],testserver` | Comma-separated host names |

See `.env.example` for a template. The real `.env` file and `db.sqlite3` are git-ignored and must not be committed.

## Deploying to production

1. Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False` and `DJANGO_ALLOWED_HOSTS`.
2. `pip install -r requirements.txt` and `python manage.py migrate`.
3. `python manage.py collectstatic --noinput`.
4. Serve the app with a WSGI server such as Gunicorn (`pip install gunicorn`, then `gunicorn config.wsgi`), behind Nginx.
5. Have Nginx serve static files straight from `STATIC_ROOT`:

```nginx
location /static/ {
    alias /path/to/household_inventory_manager/staticfiles/;
}
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

6. When the site is served over HTTPS, also enable the transport-security settings that `python manage.py check --deploy` reports (`SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`). They are left off by default so the app also runs over plain HTTP on a local machine.

SQLite is fine for a single-household app. For heavier use, switch `DATABASES` to PostgreSQL.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `ModuleNotFoundError: No module named 'django'` | Activate the virtual environment and run `pip install -r requirements.txt` |
| `no such table: inventory_location` | Run `python manage.py migrate` |
| Page has no styling with `DEBUG=False` | Run `python manage.py collectstatic` and make your web server serve `STATIC_ROOT` at `/static/` |
| `DisallowedHost` error | Add the host name to `DJANGO_ALLOWED_HOSTS` |
| An item cannot be saved | An item needs a location. Add one first |
