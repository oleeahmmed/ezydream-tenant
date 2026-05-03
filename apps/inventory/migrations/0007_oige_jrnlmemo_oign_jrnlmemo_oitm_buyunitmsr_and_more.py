# Kept as an empty migration so the merge graph stays valid.
# All real operations live in 0007_expand_inventory_b1_fields (this file duplicated
# the same AddField steps and caused "column DfltWH already exists" when both ran).

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tenant_inventory", "0006_alter_ige1_account_alter_ige1_baseentry_and_more"),
    ]

    operations = []
