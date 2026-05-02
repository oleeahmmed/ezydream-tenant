from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Client(TenantMixin):
    name = models.CharField(max_length=120)
    paid_until = models.DateField(null=True, blank=True)
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)
    auto_create_schema = True

    class Meta:
        verbose_name = "Tenant client"
        verbose_name_plural = "Tenant clients"

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    class Meta:
        verbose_name = "Domain"
        verbose_name_plural = "Domains"
