# Generated manually — SAP B1–style stub tables (OACD, OADM, …).

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenant_finance", "0002_b1_field_expansion"),
    ]

    operations = [
        migrations.CreateModel(
            name="OACD",
            fields=[
                ("AbsId", models.AutoField(primary_key=True, serialize=False)),
                ("Name", models.CharField(blank=True, default="", max_length=200, verbose_name="Name")),
            ],
            options={
                "verbose_name": "Asset class",
                "verbose_name_plural": "Asset classes (OACD)",
                "db_table": "OACD",
            },
        ),
        migrations.CreateModel(
            name="OADM",
            fields=[
                ("AbsEntry", models.AutoField(primary_key=True, serialize=False)),
                ("MainCurncy", models.CharField(blank=True, default="", max_length=3, verbose_name="Main currency")),
                ("CompnyName", models.CharField(blank=True, default="", max_length=200, verbose_name="Company name")),
            ],
            options={
                "verbose_name": "Administration setup",
                "verbose_name_plural": "Administration setup (OADM)",
                "db_table": "OADM",
            },
        ),
        migrations.CreateModel(
            name="OAGS",
            fields=[
                ("GroupCode", models.AutoField(primary_key=True, serialize=False)),
                ("GroupName", models.CharField(blank=True, default="", max_length=200, verbose_name="Group name")),
            ],
            options={
                "verbose_name": "Asset group",
                "verbose_name_plural": "Asset groups (OAGS)",
                "db_table": "OAGS",
            },
        ),
        migrations.CreateModel(
            name="OCTD",
            fields=[
                (
                    "CreditCard",
                    models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name="Credit card"),
                ),
                ("CardName", models.CharField(blank=True, default="", max_length=200, verbose_name="Card name")),
            ],
            options={
                "verbose_name": "Credit card",
                "verbose_name_plural": "Credit cards (OCTD)",
                "db_table": "OCTD",
            },
        ),
        migrations.CreateModel(
            name="OVTG",
            fields=[
                ("Code", models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name="Code")),
                ("Name", models.CharField(blank=True, default="", max_length=200, verbose_name="Name")),
                (
                    "Rate",
                    models.DecimalField(
                        decimal_places=4,
                        default=Decimal("0"),
                        max_digits=9,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0")),
                            django.core.validators.MaxValueValidator(Decimal("100")),
                        ],
                        verbose_name="Rate",
                    ),
                ),
            ],
            options={
                "verbose_name": "VAT group",
                "verbose_name_plural": "VAT groups (OVTG)",
                "db_table": "OVTG",
            },
        ),
        migrations.CreateModel(
            name="OFAV",
            fields=[
                ("AbsEntry", models.AutoField(primary_key=True, serialize=False)),
                ("AssetCode", models.CharField(blank=True, db_index=True, default="", max_length=20, verbose_name="Asset code")),
                ("CardCode", models.CharField(blank=True, db_index=True, default="", max_length=15, verbose_name="BP code")),
            ],
            options={
                "verbose_name": "Asset value",
                "verbose_name_plural": "Asset values (OFAV)",
                "db_table": "OFAV",
            },
        ),
        migrations.CreateModel(
            name="OAFR",
            fields=[
                ("AbsEntry", models.AutoField(primary_key=True, serialize=False)),
                ("AssetCode", models.CharField(blank=True, db_index=True, default="", max_length=20, verbose_name="Asset code")),
                ("PostDate", models.DateField(blank=True, null=True, verbose_name="Posting date")),
            ],
            options={
                "verbose_name": "Asset revaluation",
                "verbose_name_plural": "Asset revaluations (OAFR)",
                "db_table": "OAFR",
            },
        ),
        migrations.CreateModel(
            name="AAC1",
            fields=[
                ("Id", models.AutoField(primary_key=True, serialize=False)),
                ("ClassId", models.PositiveIntegerField(db_index=True, verbose_name="Asset class id")),
                ("AreaId", models.CharField(blank=True, db_index=True, default="", max_length=10, verbose_name="Area id")),
            ],
            options={
                "verbose_name": "Asset class depreciation area",
                "verbose_name_plural": "Asset class depreciation areas (AAC1)",
                "db_table": "AAC1",
            },
        ),
        migrations.CreateModel(
            name="ODRN",
            fields=[
                ("DocEntry", models.AutoField(primary_key=True, serialize=False)),
                ("F_RefDate", models.DateField(blank=True, null=True, verbose_name="From date")),
                ("T_RefDate", models.DateField(blank=True, null=True, verbose_name="To date")),
                ("Memo", models.CharField(blank=True, default="", max_length=200, verbose_name="Memo")),
            ],
            options={
                "verbose_name": "Depreciation run",
                "verbose_name_plural": "Depreciation runs (ODRN)",
                "db_table": "ODRN",
            },
        ),
        migrations.CreateModel(
            name="OITL",
            fields=[
                ("ReconNum", models.BigAutoField(primary_key=True, serialize=False)),
                ("CardCode", models.CharField(blank=True, db_index=True, default="", max_length=15, verbose_name="BP code")),
                ("ReconDate", models.DateField(blank=True, null=True, verbose_name="Recon date")),
            ],
            options={
                "verbose_name": "Internal reconciliation",
                "verbose_name_plural": "Internal reconciliations (OITL)",
                "db_table": "OITL",
            },
        ),
        migrations.CreateModel(
            name="ITL1",
            fields=[
                (
                    "pk",
                    models.CompositePrimaryKey(
                        "header", "LineNum", blank=True, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("LineNum", models.IntegerField(verbose_name="Line no.")),
                ("ShortName", models.CharField(blank=True, default="", max_length=50, verbose_name="Short name")),
                (
                    "Debit",
                    models.DecimalField(
                        decimal_places=6,
                        default=Decimal("0"),
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                        verbose_name="Debit",
                    ),
                ),
                (
                    "Credit",
                    models.DecimalField(
                        decimal_places=6,
                        default=Decimal("0"),
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                        verbose_name="Credit",
                    ),
                ),
                (
                    "header",
                    models.ForeignKey(
                        db_column="ReconNum",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lines",
                        to="tenant_finance.oitl",
                        verbose_name="Reconciliation",
                    ),
                ),
            ],
            options={
                "verbose_name": "Internal reconciliation line",
                "verbose_name_plural": "Internal reconciliation lines (ITL1)",
                "db_table": "ITL1",
            },
        ),
        migrations.CreateModel(
            name="OIBT",
            fields=[
                ("DocEntry", models.BigAutoField(primary_key=True, serialize=False)),
                ("TrnsfrDate", models.DateField(blank=True, null=True, verbose_name="Transfer date")),
                (
                    "TrnsfrSum",
                    models.DecimalField(
                        decimal_places=6,
                        default=Decimal("0"),
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                        verbose_name="Amount",
                    ),
                ),
                ("Memo", models.CharField(blank=True, default="", max_length=200, verbose_name="Memo")),
            ],
            options={
                "verbose_name": "Bank transfer",
                "verbose_name_plural": "Bank transfers (OIBT)",
                "db_table": "OIBT",
            },
        ),
    ]
