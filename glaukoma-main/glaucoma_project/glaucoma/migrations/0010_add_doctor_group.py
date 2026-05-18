from django.contrib.auth.models import Group
from django.db import migrations


def create_doctor_group(apps, schema_editor):
    Group.objects.get_or_create(name='doctor')


class Migration(migrations.Migration):

    dependencies = [
        ('glaucoma', '0009_remove_doctor_first_name_remove_doctor_last_name_and_more'),
    ]

    operations = [
        migrations.RunPython(
            create_doctor_group
        )
    ]
