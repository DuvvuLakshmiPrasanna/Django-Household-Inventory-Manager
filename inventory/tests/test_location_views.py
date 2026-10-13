from django.test import TestCase
from django.urls import reverse

from inventory.models import Item, Location


class LocationCrudTests(TestCase):
    def test_list_returns_200_and_shows_locations(self):
        Location.objects.create(name="Kitchen")
        response = self.client.get("/locations/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kitchen")

    def test_list_empty_state(self):
        response = self.client.get("/locations/")
        self.assertContains(response, "No locations yet")

    def test_list_shows_item_counts(self):
        loc = Location.objects.create(name="Kitchen")
        Item.objects.create(name="Kettle", location=loc)
        Item.objects.create(name="Toaster", location=loc)
        response = self.client.get("/locations/")
        self.assertEqual(response.context["locations"][0].item_count, 2)

    def test_create_get_and_post(self):
        self.assertEqual(self.client.get("/locations/add/").status_code, 200)
        response = self.client.post("/locations/add/", {"name": "Office"})
        self.assertRedirects(response, "/locations/")
        self.assertTrue(Location.objects.filter(name="Office").exists())
        self.assertContains(self.client.get("/locations/"), "Office")

    def test_create_flash_message(self):
        response = self.client.post("/locations/add/", {"name": "Office"}, follow=True)
        self.assertContains(response, "Added location")

    def test_create_empty_rerenders_with_errors(self):
        response = self.client.post("/locations/add/", {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="errorlist"')
        self.assertEqual(Location.objects.count(), 0)

    def test_create_duplicate_rejected(self):
        Location.objects.create(name="Kitchen")
        response = self.client.post("/locations/add/", {"name": "Kitchen"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")
        self.assertEqual(Location.objects.count(), 1)

    def test_create_duplicate_differing_in_case_rejected(self):
        Location.objects.create(name="Kitchen")
        response = self.client.post("/locations/add/", {"name": "kitchen"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Location.objects.count(), 1)

    def test_create_whitespace_only_rejected(self):
        response = self.client.post("/locations/add/", {"name": "   "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Location.objects.count(), 0)

    def test_update_get_and_post(self):
        loc = Location.objects.create(name="Garage")
        url = f"/locations/{loc.pk}/edit/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Garage"')
        response = self.client.post(url, {"name": "Workshop"})
        self.assertRedirects(response, "/locations/")
        loc.refresh_from_db()
        self.assertEqual(loc.name, "Workshop")

    def test_update_keeping_same_name_is_allowed(self):
        loc = Location.objects.create(name="Garage")
        response = self.client.post(f"/locations/{loc.pk}/edit/", {"name": "Garage"})
        self.assertRedirects(response, "/locations/")

    def test_update_invalid_rerenders(self):
        loc = Location.objects.create(name="Garage")
        response = self.client.post(f"/locations/{loc.pk}/edit/", {"name": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="errorlist"')

    def test_delete_get_shows_confirmation_and_keeps_object(self):
        loc = Location.objects.create(name="Attic")
        response = self.client.get(f"/locations/{loc.pk}/delete/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Attic")
        self.assertTrue(Location.objects.filter(pk=loc.pk).exists())

    def test_delete_confirmation_warns_about_items(self):
        loc = Location.objects.create(name="Attic")
        Item.objects.create(name="Box", location=loc)
        response = self.client.get(f"/locations/{loc.pk}/delete/")
        self.assertContains(response, "also deletes the 1 item ")

    def test_delete_post_removes_location_and_items(self):
        loc = Location.objects.create(name="Attic")
        Item.objects.create(name="Box", location=loc)
        response = self.client.post(f"/locations/{loc.pk}/delete/")
        self.assertRedirects(response, "/locations/")
        self.assertFalse(Location.objects.filter(pk=loc.pk).exists())
        self.assertEqual(Item.objects.count(), 0)

    def test_missing_location_returns_404(self):
        for suffix in ("edit/", "delete/"):
            self.assertEqual(self.client.get(f"/locations/999/{suffix}").status_code, 404)

    def test_url_names_resolve(self):
        self.assertEqual(reverse("inventory:location-list"), "/locations/")
        self.assertEqual(reverse("inventory:location-create"), "/locations/add/")
        self.assertEqual(reverse("inventory:location-update", args=[3]), "/locations/3/edit/")
        self.assertEqual(reverse("inventory:location-delete", args=[3]), "/locations/3/delete/")
