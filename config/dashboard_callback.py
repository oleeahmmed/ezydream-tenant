"""Unfold admin index: KPIs pulled from public schema."""

from django.db import connection


def build_admin_dashboard(request, context):
    connection.set_schema_to_public()
    from apps.core.models import Client, Domain

    context["subtitle"] = "Multitenant overview"
    context["dash_tenant_count"] = Client.objects.count()
    context["dash_domain_count"] = Domain.objects.count()
    context["dash_on_trial"] = Client.objects.filter(on_trial=True).count()
    return context
