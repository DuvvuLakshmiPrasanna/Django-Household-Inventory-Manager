"""Class-based views for locations and items (full CRUD)."""
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ItemForm, LocationForm
from .models import Item, Location


class SuccessMessageMixin:
    """Flash a message after a form is saved. Subclasses set `success_message`."""

    success_message = ""

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message.format(obj=self.object))
        return response


class DeleteMessageMixin:
    """Flash a message after an object is deleted (uses the name before deletion)."""

    success_message = ""

    def form_valid(self, form):
        label = str(self.object)
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, self.success_message.format(obj=label))
        return HttpResponseRedirect(success_url)


# --- Locations ---------------------------------------------------------------


class LocationListView(ListView):
    model = Location
    context_object_name = "locations"

    def get_queryset(self):
        return Location.objects.annotate(item_count=Count("item")).order_by("name")


class LocationCreateView(SuccessMessageMixin, CreateView):
    model = Location
    form_class = LocationForm
    success_url = reverse_lazy("inventory:location-list")
    success_message = "Added location \u201c{obj}\u201d."


class LocationUpdateView(SuccessMessageMixin, UpdateView):
    model = Location
    form_class = LocationForm
    success_url = reverse_lazy("inventory:location-list")
    success_message = "Saved changes to \u201c{obj}\u201d."


class LocationDeleteView(DeleteMessageMixin, DeleteView):
    model = Location
    success_url = reverse_lazy("inventory:location-list")
    success_message = "Deleted location \u201c{obj}\u201d and the items stored in it."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["item_count"] = self.object.item_set.count()
        return context


# --- Items -------------------------------------------------------------------


class ItemListView(ListView):
    model = Item
    context_object_name = "items"

    def get_queryset(self):
        queryset = Item.objects.select_related("location")

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        location_id = self.request.GET.get("location", "").strip()
        if location_id.isdigit():
            queryset = queryset.filter(location_id=int(location_id))

        return queryset.order_by("name", "pk")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location_id = self.request.GET.get("location", "").strip()
        context["locations"] = Location.objects.all()
        context["query"] = self.request.GET.get("q", "").strip()
        context["selected_location"] = int(location_id) if location_id.isdigit() else None
        context["is_filtered"] = bool(context["query"] or context["selected_location"])
        context["total_items"] = Item.objects.count()
        return context


class ItemFormMixin(SuccessMessageMixin):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy("inventory:item-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_locations"] = Location.objects.exists()
        return context


class ItemCreateView(ItemFormMixin, CreateView):
    success_message = "Added \u201c{obj}\u201d to your inventory."

    def get_initial(self):
        initial = super().get_initial()
        location_id = self.request.GET.get("location", "")
        if location_id.isdigit():
            initial["location"] = int(location_id)
        return initial


class ItemUpdateView(ItemFormMixin, UpdateView):
    success_message = "Saved changes to \u201c{obj}\u201d."


class ItemDeleteView(DeleteMessageMixin, DeleteView):
    model = Item
    success_url = reverse_lazy("inventory:item-list")
    success_message = "Deleted \u201c{obj}\u201d."
