from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    # Locations
    path("locations/", views.LocationListView.as_view(), name="location-list"),
    path("locations/add/", views.LocationCreateView.as_view(), name="location-create"),
    path("locations/<int:pk>/edit/", views.LocationUpdateView.as_view(), name="location-update"),
    path("locations/<int:pk>/delete/", views.LocationDeleteView.as_view(), name="location-delete"),
    # Items
    path("items/", views.ItemListView.as_view(), name="item-list"),
    path("items/add/", views.ItemCreateView.as_view(), name="item-create"),
    path("items/<int:pk>/edit/", views.ItemUpdateView.as_view(), name="item-update"),
    path("items/<int:pk>/delete/", views.ItemDeleteView.as_view(), name="item-delete"),
]
