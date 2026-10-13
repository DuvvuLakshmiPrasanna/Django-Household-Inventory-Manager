"""Data layer for the household inventory."""
from django.db import models


class Location(models.Model):
    """A place in the home where items are kept (Kitchen, Garage, ...)."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Item(models.Model):
    """Something the household owns, stored in exactly one location."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(default=1)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    class Meta:
        ordering = ["name", "pk"]

    def __str__(self):
        return self.name
