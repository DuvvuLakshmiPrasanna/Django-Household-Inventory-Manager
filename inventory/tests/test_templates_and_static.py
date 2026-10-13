"""Checks for template inheritance, the CSS architecture and static-file settings."""
import re
from pathlib import Path

from django.conf import settings
from django.template.loader import get_template
from django.test import TestCase

from inventory.models import Item, Location

APP_DIR = Path(__file__).resolve().parent.parent
STATIC_CSS = APP_DIR / "static" / "css"
TEMPLATE_DIRS = [settings.BASE_DIR / "templates", APP_DIR / "templates"]

PRIMARY_TEMPLATES = [
    "item_list.html",
    "item_form.html",
    "item_confirm_delete.html",
    "location_list.html",
    "location_form.html",
    "location_confirm_delete.html",
]


class TemplateInheritanceTests(TestCase):
    def test_base_template_exists_with_required_structure(self):
        base = settings.BASE_DIR / "templates" / "base.html"
        self.assertTrue(base.is_file())
        text = base.read_text()
        for needle in ("<html", "<head", "<body", "{% block content %}", "{% block styles %}"):
            self.assertIn(needle, text)
        head = text.split("<head", 1)[1].split("</head>", 1)[0]
        self.assertIn("{% block styles %}", head, "styles block must be inside <head>")

    def test_all_primary_templates_extend_base(self):
        for name in PRIMARY_TEMPLATES:
            path = APP_DIR / "templates" / "inventory" / name
            first_tag = path.read_text().lstrip().splitlines()[0]
            self.assertEqual(first_tag.strip(), "{% extends 'base.html' %}", name)

    def test_templates_load(self):
        for name in PRIMARY_TEMPLATES:
            get_template(f"inventory/{name}")
        get_template("404.html")


class CssArchitectureTests(TestCase):
    def test_required_directories_exist_and_are_not_empty(self):
        for sub in ("base", "components", "pages"):
            directory = STATIC_CSS / sub
            self.assertTrue(directory.is_dir(), sub)
            self.assertTrue(list(directory.glob("*.css")), f"{sub}/ has no stylesheets")

    def test_item_list_links_a_page_stylesheet(self):
        response = self.client.get("/items/")
        hrefs = re.findall(r'<link[^>]+href="([^"]+)"', response.content.decode())
        self.assertTrue(
            any(h.startswith("/static/css/pages/") and h.endswith(".css") for h in hrefs), hrefs
        )

    def test_page_styles_are_not_loaded_globally(self):
        # The item list stylesheet must only be linked from the item list page.
        self.assertNotIn("css/pages/item_list.css", (settings.BASE_DIR / "templates" / "base.html").read_text())
        response = self.client.get("/locations/")
        self.assertNotIn("pages/item_list.css", response.content.decode())

    def test_every_linked_stylesheet_exists_on_disk(self):
        Location.objects.create(name="Kitchen")
        for url in ("/items/", "/items/add/", "/locations/", "/locations/add/"):
            html = self.client.get(url).content.decode()
            for href in re.findall(r'<link[^>]+href="/static/([^"]+)"', html):
                self.assertTrue((APP_DIR / "static" / href).is_file(), f"{url} links missing {href}")

    def test_delete_pages_link_existing_stylesheets(self):
        loc = Location.objects.create(name="Kitchen")
        item = Item.objects.create(name="Kettle", location=loc)
        for url in (f"/items/{item.pk}/delete/", f"/locations/{loc.pk}/delete/"):
            html = self.client.get(url).content.decode()
            for href in re.findall(r'<link[^>]+href="/static/([^"]+)"', html):
                self.assertTrue((APP_DIR / "static" / href).is_file(), href)

    def test_focus_rule_for_input_textarea_select_defines_outline(self):
        css = "\n".join(p.read_text() for p in (APP_DIR / "static").rglob("*.css"))
        for element in ("input", "textarea", "select"):
            for pseudo in (":focus", ":focus-visible"):
                pattern = re.compile(rf"{element}{pseudo}\s*(?:,[^{{}}]*)?\{{[^}}]*outline\s*:", re.S)
                self.assertRegex(css, pattern, f"{element}{pseudo}")


class StaticSettingsTests(TestCase):
    def test_static_root_is_configured(self):
        self.assertTrue(settings.STATIC_ROOT)
        self.assertEqual(Path(settings.STATIC_ROOT), settings.BASE_DIR / "staticfiles")
        self.assertEqual(settings.STATIC_URL, "/static/")

    def test_settings_file_defines_static_root_uncommented(self):
        text = (settings.BASE_DIR / "config" / "settings.py").read_text()
        self.assertRegex(text, r"(?m)^STATIC_ROOT\s*=\s*BASE_DIR\s*/\s*['\"]staticfiles['\"]")


class ProjectFilesTests(TestCase):
    def test_readme_mentions_required_commands(self):
        text = (settings.BASE_DIR / "README.md").read_text()
        for keyword in ("requirements.txt", "migrate", "runserver", "collectstatic"):
            self.assertIn(keyword, text)

    def test_requirements_file_lists_django(self):
        text = (settings.BASE_DIR / "requirements.txt").read_text().lower()
        self.assertIn("django", text)

    def test_custom_404_page(self):
        with self.settings(DEBUG=False):
            response = self.client.get("/does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page not found", status_code=404)
