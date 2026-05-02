"""Shared Unfold ``ModelAdmin`` defaults for ERP apps (django-unfold 0.65.x)."""

from unfold.admin import ModelAdmin


class ErpModelAdmin(ModelAdmin):
    """Consistent Unfold change list / form UX for SAP-style models."""

    compressed_fields = True
    warn_unsaved_form = True
