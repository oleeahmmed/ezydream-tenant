# SAP-style BOM: ProductBom header + ProductBomLine (position, UoM, scrap, …).
# Migrates legacy flat lines (parent_product on each row) into one header per parent material.

from collections import defaultdict
from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models
from django.utils import timezone


def migrate_legacy_bom_lines(apps, schema_editor):
    Product = apps.get_model("tenant_foundation", "Product")
    ProductBom = apps.get_model("tenant_foundation", "ProductBom")
    ProductBomLine = apps.get_model("tenant_foundation", "ProductBomLine")

    lines = list(ProductBomLine.objects.all().order_by("parent_product_id", "id"))
    if not lines:
        return

    today = timezone.localdate()
    grouped = defaultdict(list)
    for row in lines:
        grouped[row.parent_product_id].append(row)

    for parent_id, lst in grouped.items():
        p = Product.objects.get(pk=parent_id)
        base = f"MIG-{p.code}"[:50]
        code = base
        suffix_n = 1
        while ProductBom.objects.filter(code=code).exists():
            suffix_n += 1
            suffix = f"-{suffix_n}"
            code = f"{base[: max(1, 50 - len(suffix))]}{suffix}"
        bom = ProductBom(
            code=code,
            name=(f"Migrated BOM ({p.code})")[:200],
            parent_product_id=parent_id,
            warehouse_id=None,
            usage="1",
            alternative=1,
            valid_from=today,
            valid_to=None,
            is_active=True,
        )
        bom.save()
        for idx, line in enumerate(lst):
            line.bom_id = bom.pk
            line.position = (idx + 1) * 10
            line.save(update_fields=["bom_id", "position", "updated_at"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("tenant_foundation", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductBom",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "code",
                    models.CharField(
                        db_index=True,
                        help_text="BOM number / document id (unique in schema).",
                        max_length=50,
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=200)),
                (
                    "usage",
                    models.CharField(
                        choices=[("1", "Production"), ("2", "Costing"), ("3", "Engineering")],
                        db_index=True,
                        default="1",
                        max_length=1,
                    ),
                ),
                (
                    "alternative",
                    models.PositiveSmallIntegerField(default=1, help_text="Alternative BOM (STALT)."),
                ),
                (
                    "valid_from",
                    models.DateField(default=timezone.localdate, help_text="BOM valid-from date."),
                ),
                ("valid_to", models.DateField(blank=True, help_text="Blank = open-ended.", null=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "parent_product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="boms",
                        to="tenant_foundation.product",
                    ),
                ),
                (
                    "warehouse",
                    models.ForeignKey(
                        blank=True,
                        help_text="Optional plant (Werks). Empty = not restricted to one warehouse.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="boms",
                        to="tenant_foundation.warehouse",
                    ),
                ),
            ],
            options={
                "ordering": ["parent_product", "alternative", "code"],
            },
        ),
        migrations.AddIndex(
            model_name="productbom",
            index=models.Index(fields=["parent_product", "is_active"], name="f1_bomhdr_par_ix"),
        ),
        migrations.AddConstraint(
            model_name="productbom",
            constraint=models.UniqueConstraint(fields=("code",), name="f1_bomhdr_code_uq"),
        ),
        migrations.AddConstraint(
            model_name="productbom",
            constraint=models.UniqueConstraint(
                condition=models.Q(warehouse__isnull=True),
                fields=("parent_product", "alternative", "usage"),
                name="f1_bomhdr_nopwh_uq",
            ),
        ),
        migrations.AddConstraint(
            model_name="productbom",
            constraint=models.UniqueConstraint(
                condition=models.Q(warehouse__isnull=False),
                fields=("parent_product", "warehouse", "alternative", "usage"),
                name="f1_bomhdr_wh_uq",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="productbomline",
            name="f1_bom_par_comp_uq",
        ),
        migrations.AddField(
            model_name="productbomline",
            name="bom",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="lines",
                to="tenant_foundation.productbom",
            ),
        ),
        migrations.AddField(
            model_name="productbomline",
            name="position",
            field=models.PositiveIntegerField(
                default=10,
                help_text="Item number (e.g. 10, 20, 30 — like STPO position).",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="productbomline",
            name="component_uom",
            field=models.ForeignKey(
                blank=True,
                help_text="Component UoM; empty = use component material default UoM.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bom_line_components",
                to="tenant_foundation.unitofmeasure",
            ),
        ),
        migrations.AddField(
            model_name="productbomline",
            name="scrap_percent",
            field=models.DecimalField(
                decimal_places=4,
                default=Decimal("0"),
                help_text="Component scrap % (SAP-style).",
                max_digits=7,
                validators=[
                    django.core.validators.MinValueValidator(Decimal("0")),
                    django.core.validators.MaxValueValidator(Decimal("100")),
                ],
            ),
        ),
        migrations.AddField(
            model_name="productbomline",
            name="item_text",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="productbomline",
            name="valid_from",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="productbomline",
            name="valid_to",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RunPython(migrate_legacy_bom_lines, noop_reverse),
        migrations.AlterField(
            model_name="productbomline",
            name="bom",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="lines",
                to="tenant_foundation.productbom",
            ),
        ),
        migrations.RemoveField(
            model_name="productbomline",
            name="parent_product",
        ),
        migrations.AlterField(
            model_name="productbomline",
            name="component_product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="used_in_bom_lines",
                to="tenant_foundation.product",
            ),
        ),
        migrations.AlterField(
            model_name="productbomline",
            name="quantity",
            field=models.DecimalField(
                decimal_places=8,
                help_text="Component quantity per 1 unit of header material.",
                max_digits=18,
                validators=[django.core.validators.MinValueValidator(Decimal("0"))],
            ),
        ),
        migrations.AlterModelOptions(
            name="productbomline",
            options={"ordering": ["bom", "position"]},
        ),
        migrations.AddConstraint(
            model_name="productbomline",
            constraint=models.UniqueConstraint(fields=("bom", "position"), name="f1_bomln_bom_pos_uq"),
        ),
        migrations.AddIndex(
            model_name="productbomline",
            index=models.Index(fields=["bom", "component_product"], name="f1_bomln_bom_cmp_ix"),
        ),
    ]
