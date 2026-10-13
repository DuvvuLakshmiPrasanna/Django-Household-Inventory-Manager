"""ModelForms for creating and editing locations and items."""
from django import forms

from .models import Item, Location


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"autocomplete": "off"})}

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Enter a location name.")
        # The database enforces exact uniqueness; also reject "kitchen" vs "Kitchen".
        duplicates = Location.objects.filter(name__iexact=name)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("A location with this name already exists.")
        return name


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "description", "quantity", "location"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "quantity": forms.NumberInput(attrs={"min": 0}),
        }
        help_texts = {
            "description": "Optional. Brand, size, or where exactly it is stored.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["location"].empty_label = "Choose a location"

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Enter an item name.")
        return name

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        return quantity
