from django.test import TestCase
from django.urls import reverse

from inventory.models import Item, Location


class ItemCrudTests(TestCase):
    def setUp(self):
        self.kitchen = Location.objects.create(name="Kitchen")
        self.garage = Location.objects.create(name="Garage")

    def test_list_returns_200_and_shows_items(self):
        Item.objects.create(name="Kettle", quantity=2, location=self.kitchen)
        response = self.client.get("/items/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kettle")
        self.assertContains(response, "Kitchen")

    def test_list_empty_state(self):
        self.assertContains(self.client.get("/items/"), "No items yet")

    def test_list_empty_state_without_locations(self):
        Location.objects.all().delete()
        self.assertContains(self.client.get("/items/"), "Create a location first")

    def test_home_redirects_to_items(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/items/")

    def test_create_get_and_post(self):
        self.assertEqual(self.client.get("/items/add/").status_code, 200)
        response = self.client.post(
            "/items/add/",
            {"name": "Drill", "description": "18V cordless", "quantity": 1, "location": self.garage.pk},
        )
        self.assertRedirects(response, "/items/")
        item = Item.objects.get(name="Drill")
        self.assertEqual(item.location, self.garage)
        self.assertEqual(item.description, "18V cordless")
        self.assertContains(self.client.get("/items/"), "Drill")

    def test_create_description_is_optional_and_quantity_required(self):
        response = self.client.post(
            "/items/add/", {"name": "Spoon", "quantity": 12, "location": self.kitchen.pk}
        )
        self.assertRedirects(response, "/items/")
        self.assertEqual(Item.objects.get(name="Spoon").description, "")

    def test_create_prefills_location_from_query_string(self):
        response = self.client.get(f"/items/add/?location={self.garage.pk}")
        self.assertEqual(response.context["form"].initial["location"], self.garage.pk)

    def test_create_ignores_bad_location_query_string(self):
        self.assertEqual(self.client.get("/items/add/?location=abc").status_code, 200)

    def test_create_with_empty_body_rerenders_with_errors(self):
        response = self.client.post("/items/add/", {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<ul class="errorlist"')
        self.assertContains(response, "This field is required.")
        self.assertEqual(Item.objects.count(), 0)

    def test_errors_are_next_to_the_field_and_linked_for_screen_readers(self):
        response = self.client.post("/items/add/", {})
        html = response.content.decode()
        self.assertIn('id="id_name_error"', html)
        self.assertIn('aria-describedby="id_name_error"', html)
        self.assertIn('aria-invalid="true"', html)

    def test_create_rejects_negative_quantity(self):
        response = self.client.post(
            "/items/add/", {"name": "Bolt", "quantity": -1, "location": self.garage.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot be negative")

    def test_create_rejects_non_numeric_quantity(self):
        response = self.client.post(
            "/items/add/", {"name": "Bolt", "quantity": "lots", "location": self.garage.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Item.objects.count(), 0)

    def test_create_rejects_unknown_location(self):
        response = self.client.post(
            "/items/add/", {"name": "Bolt", "quantity": 1, "location": 9999}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice")

    def test_create_rejects_overlong_name(self):
        response = self.client.post(
            "/items/add/", {"name": "x" * 101, "quantity": 1, "location": self.garage.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Item.objects.count(), 0)

    def test_create_page_warns_when_no_locations(self):
        Location.objects.all().delete()
        self.assertContains(self.client.get("/items/add/"), "Add a location first")

    def test_every_field_has_a_label(self):
        html = self.client.get("/items/add/").content.decode()
        for field_id in ("id_name", "id_description", "id_quantity", "id_location"):
            self.assertIn(f'for="{field_id}"', html)
            self.assertIn(f'id="{field_id}"', html)

    def test_update_get_and_post(self):
        item = Item.objects.create(name="Kettle", quantity=1, location=self.kitchen)
        url = f"/items/{item.pk}/edit/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Kettle"')
        response = self.client.post(
            url, {"name": "Electric kettle", "description": "", "quantity": 3, "location": self.garage.pk}
        )
        self.assertRedirects(response, "/items/")
        item.refresh_from_db()
        self.assertEqual((item.name, item.quantity, item.location), ("Electric kettle", 3, self.garage))

    def test_update_invalid_rerenders(self):
        item = Item.objects.create(name="Kettle", location=self.kitchen)
        response = self.client.post(f"/items/{item.pk}/edit/", {"name": "", "quantity": 1, "location": self.kitchen.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="errorlist"')

    def test_delete_get_shows_confirmation_and_keeps_object(self):
        item = Item.objects.create(name="Kettle", location=self.kitchen)
        response = self.client.get(f"/items/{item.pk}/delete/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kettle")
        self.assertTrue(Item.objects.filter(pk=item.pk).exists())

    def test_delete_post_removes_item(self):
        item = Item.objects.create(name="Kettle", location=self.kitchen)
        response = self.client.post(f"/items/{item.pk}/delete/")
        self.assertRedirects(response, "/items/")
        self.assertFalse(Item.objects.filter(pk=item.pk).exists())
        self.assertTrue(Location.objects.filter(pk=self.kitchen.pk).exists())

    def test_delete_flash_message_names_the_item(self):
        item = Item.objects.create(name="Kettle", location=self.kitchen)
        response = self.client.post(f"/items/{item.pk}/delete/", follow=True)
        self.assertContains(response, "Deleted \u201cKettle\u201d")

    def test_missing_item_returns_404(self):
        for suffix in ("edit/", "delete/"):
            self.assertEqual(self.client.get(f"/items/999/{suffix}").status_code, 404)

    def test_url_names_resolve(self):
        self.assertEqual(reverse("inventory:item-list"), "/items/")
        self.assertEqual(reverse("inventory:item-create"), "/items/add/")
        self.assertEqual(reverse("inventory:item-update", args=[1]), "/items/1/edit/")
        self.assertEqual(reverse("inventory:item-delete", args=[1]), "/items/1/delete/")


class ItemListFilterTests(TestCase):
    def setUp(self):
        self.kitchen = Location.objects.create(name="Kitchen")
        self.garage = Location.objects.create(name="Garage")
        Item.objects.create(name="Kettle", description="Stainless steel", location=self.kitchen)
        Item.objects.create(name="Drill", description="Cordless", location=self.garage)

    def test_filter_by_location(self):
        response = self.client.get(f"/items/?location={self.garage.pk}")
        self.assertEqual([i.name for i in response.context["items"]], ["Drill"])

    def test_search_by_name_and_description(self):
        by_name = self.client.get("/items/?q=kett")
        self.assertEqual([i.name for i in by_name.context["items"]], ["Kettle"])
        by_description = self.client.get("/items/?q=cordless")
        self.assertEqual([i.name for i in by_description.context["items"]], ["Drill"])

    def test_filters_combine(self):
        response = self.client.get(f"/items/?q=drill&location={self.kitchen.pk}")
        self.assertEqual(len(response.context["items"]), 0)
        self.assertContains(response, "No items match")

    def test_bad_location_value_is_ignored(self):
        response = self.client.get("/items/?location=abc")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["items"]), 2)

    def test_items_sorted_by_name(self):
        response = self.client.get("/items/")
        self.assertEqual([i.name for i in response.context["items"]], ["Drill", "Kettle"])

    def test_list_does_not_query_per_row(self):
        for n in range(10):
            Item.objects.create(name=f"Thing {n}", location=self.kitchen)
        # item count + location list + items (joined with their location) = 3 queries,
        # regardless of how many rows are shown.
        with self.assertNumQueries(3):
            self.client.get("/items/")
