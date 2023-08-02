from django.db import migrations


def create_superuser(apps, schema_editor):
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin'
        )


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.RunPython(create_superuser),
    ]


