# Generated manually — SAP-style Canceled (Y/N) for soft delete on headers and lines.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tenant_sales", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="oqut",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="qut1",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="ordr",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="rdr1",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="odln",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="dln1",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="ordn",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="rdn1",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="oinv",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
        migrations.AddField(
            model_name="inv1",
            name="Canceled",
            field=models.CharField(
                "Canceled (Y/N)", db_index=True, default="N", max_length=1
            ),
        ),
    ]
