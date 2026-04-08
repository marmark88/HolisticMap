# Generated manually to enforce non-null user links.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def purge_legacy_role_rows(apps, schema_editor):
    Executive = apps.get_model("holisticmap", "Executive")
    Employee = apps.get_model("holisticmap", "Employee")
    Employer = apps.get_model("holisticmap", "Employer")

    # Remove pre-auth rows that cannot satisfy required user FK/O2O.
    Employee.objects.all().delete()
    Employer.objects.all().delete()
    Executive.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("holisticmap", "0005_rename_join_secret_hash_company_employee_secret_hash_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="executive",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="employee",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="employer",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(purge_legacy_role_rows, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="executive",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="employee",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="employer",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
