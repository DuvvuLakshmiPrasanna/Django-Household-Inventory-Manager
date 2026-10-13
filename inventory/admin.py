from django.contrib import admin

from .models import Item, Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "quantity", "location"]
    list_filter = ["location"]
    search_fields = ["name", "description"]
