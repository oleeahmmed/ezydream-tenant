"""Bolt metadata endpoints (field choice catalog for dropdowns)."""

from __future__ import annotations

from django_bolt import BoltAPI
from django_bolt.auth import IsAuthenticated, JWTAuthentication
from django_bolt.request import Request
from django_bolt.views import APIView

from apps.core.b1_field_choices import field_choice_catalog_for_api

META_API_PREFIX = "/api/meta"


class FieldChoicesListView(APIView):
    """Return persisted code values + human labels + field→group hints for the SPA."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, request: Request) -> dict:
        return field_choice_catalog_for_api()


def attach_core_routes(api: BoltAPI) -> None:
    tag = ["meta"]
    api.view(META_API_PREFIX + "/field-choices", methods=["GET"], status_code=200, tags=tag)(FieldChoicesListView)
