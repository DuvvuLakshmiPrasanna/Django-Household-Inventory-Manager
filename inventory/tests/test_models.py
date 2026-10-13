from django.db import IntegrityError, transaction
from django.test import TestCase

from inventory.models import Item, Location


class LocationModelTests(TestCase):
    def test_name_field_options(self):
        field = Location._meta.get_field("name")
        self.assertEqual(field.max_length, 100)
        self.assertTrue(field.unique)

    def test_str_returns_name(self):
        self.assertEqual(str(Location(name="Kitchen")), "Kitchen")

    def test_name_must_be_unique(self):
        Location.objects.create(name="Kitchen")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Location.objects.create(name="Kitchen")


class ItemModelTests(TestCase):
    def setUp(self):
        self.location = Location.objects.create(name="Garage")

    def test_field_options(self):
        meta = Item._meta
        self.assertEqual(meta.get_field("name").max_length, 100)
        self.assertTrue(meta.get_field("description").blank)
        self.assertEqual(meta.get_field("quantity").default, 1)
        fk = meta.get_field("location")
        self.assertIs(fk.related_model, Location)
        self.assertEqual(fk.remote_field.on_delete.__name__, "CASCADE")

    def test_defaults(self):
        item = Item.objects.create(name="Ladder", location=self.location)
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.description, "")

    def test_deleting_location_cascades_to_items(self):
        Item.objects.create(name="Ladder", location=self.location)
        self.location.delete()
        self.assertEqual(Item.objects.count(), 0)
