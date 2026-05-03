# Generated manually for SAP B1–aligned inventory fields.
#
# Database changes use IF NOT EXISTS so this migration still applies cleanly when an
# older duplicate migration (0007_oige_...) already created the same columns.

import django.core.validators
from decimal import Decimal
from django.db import migrations, models


def _expand_inventory_b1_fields_forwards(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != "postgresql":
        raise NotImplementedError(
            "tenant_inventory.0007_expand_inventory_b1_fields requires PostgreSQL"
        )
    # Mirrors `sqlmigrate tenant_inventory 0007_expand_inventory_b1_fields`, with
    # ADD COLUMN IF NOT EXISTS and CREATE INDEX IF NOT EXISTS for idempotency.
    stmts = [
        'ALTER TABLE "OITM" ADD COLUMN IF NOT EXISTS "DfltWH" varchar(20) DEFAULT \'\' NOT NULL;',
        'ALTER TABLE "OITM" ALTER COLUMN "DfltWH" DROP DEFAULT;',
        'ALTER TABLE "OITM" ADD COLUMN IF NOT EXISTS "FrgnName" varchar(200) DEFAULT \'\' NOT NULL;',
        'ALTER TABLE "OITM" ALTER COLUMN "FrgnName" DROP DEFAULT;',
        'ALTER TABLE "OITM" ADD COLUMN IF NOT EXISTS "CodeBars" varchar(200) DEFAULT \'\' NOT NULL;',
        'ALTER TABLE "OITM" ALTER COLUMN "CodeBars" DROP DEFAULT;',
        'ALTER TABLE "OITM" ADD COLUMN IF NOT EXISTS "SalItem" varchar(1) DEFAULT \'Y\' NOT NULL;',
        'ALTER TABLE "OITM" ALTER COLUMN "SalItem" DROP DEFAULT;',
        'ALTER TABLE "OITM" ADD COLUMN IF NOT EXISTS "PrchseItem" varchar(1) DEFAULT \'Y\' NOT NULL;',
        'ALTER TABLE "OITM" ALTER COLUMN "PrchseItem" DROP DEFAULT;',
        'ALTER TABLE "OITM" ADD COLUMN IF NOT EXISTS "SalUnitMsr" varchar(100) DEFAULT \'\' NOT NULL;',
        'ALTER TABLE "OITM" ALTER COLUMN "SalUnitMsr" DROP DEFAULT;',
        'ALTER TABLE "OITM" ADD COLUMN IF NOT EXISTS "BuyUnitMsr" varchar(100) DEFAULT \'\' NOT NULL;',
        'ALTER TABLE "OITM" ALTER COLUMN "BuyUnitMsr" DROP DEFAULT;',
        'ALTER TABLE "OITW" ADD COLUMN IF NOT EXISTS "OrderQty" numeric(19, 6) DEFAULT 0 NOT NULL;',
        'ALTER TABLE "OITW" ALTER COLUMN "OrderQty" DROP DEFAULT;',
        'ALTER TABLE "OITW" ADD COLUMN IF NOT EXISTS "MinStock" numeric(19, 6) DEFAULT 0 NOT NULL;',
        'ALTER TABLE "OITW" ALTER COLUMN "MinStock" DROP DEFAULT;',
        'ALTER TABLE "OITW" ADD COLUMN IF NOT EXISTS "MaxStock" numeric(19, 6) DEFAULT 0 NOT NULL;',
        'ALTER TABLE "OITW" ALTER COLUMN "MaxStock" DROP DEFAULT;',
        'ALTER TABLE "OITW" ADD COLUMN IF NOT EXISTS "Locked" varchar(1) DEFAULT \'N\' NOT NULL;',
        'ALTER TABLE "OITW" ALTER COLUMN "Locked" DROP DEFAULT;',
        'ALTER TABLE "OWTQ" ADD COLUMN IF NOT EXISTS "JrnlMemo" text DEFAULT \'\' NOT NULL;',
        'ALTER TABLE "OWTQ" ALTER COLUMN "JrnlMemo" DROP DEFAULT;',
        'ALTER TABLE "OWTR" ADD COLUMN IF NOT EXISTS "JrnlMemo" text DEFAULT \'\' NOT NULL;',
        'ALTER TABLE "OWTR" ALTER COLUMN "JrnlMemo" DROP DEFAULT;',
        'ALTER TABLE "OIGN" ADD COLUMN IF NOT EXISTS "JrnlMemo" text DEFAULT \'\' NOT NULL;',
        'ALTER TABLE "OIGN" ALTER COLUMN "JrnlMemo" DROP DEFAULT;',
        'ALTER TABLE "OIGE" ADD COLUMN IF NOT EXISTS "JrnlMemo" text DEFAULT \'\' NOT NULL;',
        'ALTER TABLE "OIGE" ALTER COLUMN "JrnlMemo" DROP DEFAULT;',
        'ALTER TABLE "WTQ1" ADD COLUMN IF NOT EXISTS "BaseLine" integer NULL;',
        'ALTER TABLE "WTQ1" ALTER COLUMN "FromWhsCod" TYPE varchar(20);',
        'ALTER TABLE "WTQ1" ALTER COLUMN "WhsCode" TYPE varchar(20);',
        'ALTER TABLE "WTR1" ADD COLUMN IF NOT EXISTS "FromWhsCod" varchar(20) DEFAULT \'\' NOT NULL;',
        'ALTER TABLE "WTR1" ALTER COLUMN "FromWhsCod" DROP DEFAULT;',
        'CREATE INDEX IF NOT EXISTS "wtr1_fromwhs_ix" ON "WTR1" ("FromWhsCod");',
        'CREATE INDEX IF NOT EXISTS "OITM_DfltWH_e6cc8812" ON "OITM" ("DfltWH");',
        'CREATE INDEX IF NOT EXISTS "OITM_DfltWH_e6cc8812_like" ON "OITM" ("DfltWH" varchar_pattern_ops);',
        'CREATE INDEX IF NOT EXISTS "OITM_CodeBars_05dae2bf" ON "OITM" ("CodeBars");',
        'CREATE INDEX IF NOT EXISTS "OITM_CodeBars_05dae2bf_like" ON "OITM" ("CodeBars" varchar_pattern_ops);',
        'CREATE INDEX IF NOT EXISTS "OITM_SalItem_8c106fc6" ON "OITM" ("SalItem");',
        'CREATE INDEX IF NOT EXISTS "OITM_SalItem_8c106fc6_like" ON "OITM" ("SalItem" varchar_pattern_ops);',
        'CREATE INDEX IF NOT EXISTS "OITM_PrchseItem_650b5cf0" ON "OITM" ("PrchseItem");',
        'CREATE INDEX IF NOT EXISTS "OITM_PrchseItem_650b5cf0_like" ON "OITM" ("PrchseItem" varchar_pattern_ops);',
        'CREATE INDEX IF NOT EXISTS "OITW_Locked_da49a4fe" ON "OITW" ("Locked");',
        'CREATE INDEX IF NOT EXISTS "OITW_Locked_da49a4fe_like" ON "OITW" ("Locked" varchar_pattern_ops);',
        'CREATE INDEX IF NOT EXISTS "WTQ1_BaseLine_2eb27456" ON "WTQ1" ("BaseLine");',
        'CREATE INDEX IF NOT EXISTS "WTR1_FromWhsCod_7db312c1" ON "WTR1" ("FromWhsCod");',
        'CREATE INDEX IF NOT EXISTS "WTR1_FromWhsCod_7db312c1_like" ON "WTR1" ("FromWhsCod" varchar_pattern_ops);',
    ]
    with connection.cursor() as cursor:
        for sql in stmts:
            cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ("tenant_inventory", "0006_alter_ige1_account_alter_ige1_baseentry_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    _expand_inventory_b1_fields_forwards,
                    migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="oitm",
                    name="DfltWH",
                    field=models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        max_length=20,
                        verbose_name="Default Warehouse",
                    ),
                ),
                migrations.AddField(
                    model_name="oitm",
                    name="FrgnName",
                    field=models.CharField(
                        blank=True, default="", max_length=200, verbose_name="Foreign Name"
                    ),
                ),
                migrations.AddField(
                    model_name="oitm",
                    name="CodeBars",
                    field=models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        max_length=200,
                        verbose_name="Bar Code",
                    ),
                ),
                migrations.AddField(
                    model_name="oitm",
                    name="SalItem",
                    field=models.CharField(
                        db_index=True, default="Y", max_length=1, verbose_name="Sales Item"
                    ),
                ),
                migrations.AddField(
                    model_name="oitm",
                    name="PrchseItem",
                    field=models.CharField(
                        db_index=True, default="Y", max_length=1, verbose_name="Purchase Item"
                    ),
                ),
                migrations.AddField(
                    model_name="oitm",
                    name="SalUnitMsr",
                    field=models.CharField(
                        blank=True, default="", max_length=100, verbose_name="Sales UoM"
                    ),
                ),
                migrations.AddField(
                    model_name="oitm",
                    name="BuyUnitMsr",
                    field=models.CharField(
                        blank=True, default="", max_length=100, verbose_name="Purchasing UoM"
                    ),
                ),
                migrations.AddField(
                    model_name="oitw",
                    name="OrderQty",
                    field=models.DecimalField(
                        decimal_places=6,
                        default=Decimal("0"),
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                        verbose_name="Ordered (Warehouse)",
                    ),
                ),
                migrations.AddField(
                    model_name="oitw",
                    name="MinStock",
                    field=models.DecimalField(
                        decimal_places=6,
                        default=Decimal("0"),
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                        verbose_name="Minimum Stock",
                    ),
                ),
                migrations.AddField(
                    model_name="oitw",
                    name="MaxStock",
                    field=models.DecimalField(
                        decimal_places=6,
                        default=Decimal("0"),
                        max_digits=19,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                        verbose_name="Maximum Stock",
                    ),
                ),
                migrations.AddField(
                    model_name="oitw",
                    name="Locked",
                    field=models.CharField(
                        db_index=True,
                        default="N",
                        max_length=1,
                        verbose_name="Locked (Warehouse Row)",
                    ),
                ),
                migrations.AddField(
                    model_name="owtq",
                    name="JrnlMemo",
                    field=models.TextField(blank=True, default="", verbose_name="Memo"),
                ),
                migrations.AddField(
                    model_name="owtr",
                    name="JrnlMemo",
                    field=models.TextField(blank=True, default="", verbose_name="Memo"),
                ),
                migrations.AddField(
                    model_name="oign",
                    name="JrnlMemo",
                    field=models.TextField(blank=True, default="", verbose_name="Memo"),
                ),
                migrations.AddField(
                    model_name="oige",
                    name="JrnlMemo",
                    field=models.TextField(blank=True, default="", verbose_name="Memo"),
                ),
                migrations.AddField(
                    model_name="wtq1",
                    name="BaseLine",
                    field=models.IntegerField(
                        blank=True, db_index=True, null=True, verbose_name="Base Row"
                    ),
                ),
                migrations.AlterField(
                    model_name="wtq1",
                    name="FromWhsCod",
                    field=models.CharField(
                        db_index=True, max_length=20, verbose_name="From Warehouse"
                    ),
                ),
                migrations.AlterField(
                    model_name="wtq1",
                    name="WhsCode",
                    field=models.CharField(db_index=True, max_length=20, verbose_name="Warehouse"),
                ),
                migrations.AddField(
                    model_name="wtr1",
                    name="FromWhsCod",
                    field=models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        max_length=20,
                        verbose_name="From Warehouse",
                    ),
                ),
                migrations.AddIndex(
                    model_name="wtr1",
                    index=models.Index(fields=["FromWhsCod"], name="wtr1_fromwhs_ix"),
                ),
            ],
        ),
    ]
