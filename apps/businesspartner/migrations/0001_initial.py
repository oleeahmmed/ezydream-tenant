# Generated manually for tenant_businesspartner (OCRG, OCRD, CRD1).

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="OCRG",
            fields=[
                ("GroupCode", models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ("GroupName", models.CharField(db_index=True, max_length=100)),
                ("GroupType", models.CharField(db_index=True, default="B", max_length=1)),
                ("Canceled", models.CharField(db_index=True, default="N", max_length=1)),
            ],
            options={
                "db_table": "OCRG",
            },
        ),
        migrations.CreateModel(
            name="OCRD",
            fields=[
                ("CardCode", models.CharField(max_length=15, primary_key=True, serialize=False)),
                ("CardName", models.CharField(db_index=True, max_length=200)),
                ("CardType", models.CharField(db_index=True, default="C", max_length=1)),
                ("CardFName", models.CharField(blank=True, default="", max_length=200)),
                ("CntctPrsn", models.CharField(blank=True, db_index=True, default="", max_length=100)),
                ("Phone1", models.CharField(blank=True, default="", max_length=50)),
                ("Phone2", models.CharField(blank=True, default="", max_length=50)),
                ("Fax", models.CharField(blank=True, default="", max_length=50)),
                ("Cellular", models.CharField(blank=True, default="", max_length=50)),
                ("E_Mail", models.CharField(blank=True, db_index=True, default="", max_length=100)),
                ("Website", models.CharField(blank=True, default="", max_length=100)),
                ("LicTradNum", models.CharField(blank=True, db_index=True, default="", max_length=32)),
                (
                    "CreditLine",
                    models.DecimalField(
                        decimal_places=6,
                        default=Decimal("0"),
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                    ),
                ),
                (
                    "DebtLine",
                    models.DecimalField(
                        decimal_places=6,
                        default=Decimal("0"),
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                    ),
                ),
                ("Balance", models.DecimalField(decimal_places=6, default=Decimal("0"), max_digits=19)),
                (
                    "OrdersBal",
                    models.DecimalField(
                        decimal_places=6,
                        default=Decimal("0"),
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                    ),
                ),
                (
                    "DNotesBal",
                    models.DecimalField(
                        decimal_places=6,
                        default=Decimal("0"),
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                    ),
                ),
                ("Currency", models.CharField(blank=True, db_index=True, default="", max_length=15)),
                ("PayTermsGrpCode", models.IntegerField(blank=True, db_index=True, null=True)),
                ("DfltWhs", models.CharField(blank=True, db_index=True, default="", max_length=20)),
                ("ShipToDef", models.CharField(blank=True, default="", max_length=50)),
                ("BillToDef", models.CharField(blank=True, default="", max_length=50)),
                ("SlpCode", models.IntegerField(blank=True, db_index=True, null=True)),
                ("Comments", models.TextField(blank=True, default="")),
                ("ValidFor", models.CharField(db_index=True, default="Y", max_length=1)),
                ("Frozen", models.CharField(db_index=True, default="N", max_length=1)),
                ("Canceled", models.CharField(db_index=True, default="N", max_length=1)),
                (
                    "GroupCode",
                    models.ForeignKey(
                        blank=True,
                        db_column="GroupCode",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="partners",
                        to="tenant_businesspartner.ocrg",
                    ),
                ),
            ],
            options={
                "db_table": "OCRD",
                "indexes": [models.Index(fields=["CardName"], name="ocrd_cardname_ix")],
            },
        ),
        migrations.CreateModel(
            name="CRD1",
            fields=[
                ("pk", models.CompositePrimaryKey("header", "Address", blank=True, editable=False, primary_key=True, serialize=False)),
                ("Address", models.CharField(db_index=True, max_length=50)),
                ("Street", models.CharField(blank=True, default="", max_length=100)),
                ("Block", models.CharField(blank=True, default="", max_length=100)),
                ("City", models.CharField(blank=True, db_index=True, default="", max_length=100)),
                ("County", models.CharField(blank=True, default="", max_length=100)),
                ("ZipCode", models.CharField(blank=True, default="", max_length=20)),
                ("Country", models.CharField(blank=True, db_index=True, default="", max_length=3)),
                ("State", models.CharField(blank=True, default="", max_length=3)),
                ("Building", models.CharField(blank=True, default="", max_length=100)),
                ("AdresType", models.CharField(db_index=True, default="S", max_length=1)),
                ("Canceled", models.CharField(db_index=True, default="N", max_length=1)),
                (
                    "header",
                    models.ForeignKey(
                        db_column="CardCode",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="addresses",
                        to="tenant_businesspartner.ocrd",
                    ),
                ),
            ],
            options={
                "db_table": "CRD1",
                "indexes": [models.Index(fields=["City"], name="crd1_city_ix")],
            },
        ),
    ]
