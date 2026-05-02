# Canceled / ValidFor flags for soft delete and inactive items (SAP-style).

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenant_inventory", "0003_alter_ige1_options_alter_ign1_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="oitb",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="oitm",
            name="ValidFor",
            field=models.CharField(
                "Valid for (Y/N)", db_index=True, default="Y", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="oitw",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="owtq",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="wtq1",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="owtr",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="wtr1",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="oign",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="ign1",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="oige",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="ige1",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="oinc",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="inc1",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="oinm",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
    ]
