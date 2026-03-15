from django.db import migrations, models


def normalize_okr_statuses(apps, schema_editor):
    Okr = apps.get_model('okr', 'Okr')
    KeyResult = apps.get_model('okr', 'KeyResult')

    status_mapping = {
        'active': 'on_track',
        'off_track': 'at_risk',
        'archived': 'completed',
    }

    for old_status, new_status in status_mapping.items():
        Okr.objects.filter(status=old_status).update(status=new_status)
        KeyResult.objects.filter(status=old_status).update(status=new_status)


class Migration(migrations.Migration):
    dependencies = [
        ('okr', '0006_remove_keyresult_progress'),
    ]

    operations = [
        migrations.RunPython(normalize_okr_statuses, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='okr',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Черновик'),
                    ('on_track', 'В графике'),
                    ('at_risk', 'Под риском'),
                    ('completed', 'Завершён'),
                ],
                default='draft',
                max_length=32,
                verbose_name='Статус',
            ),
        ),
        migrations.AlterField(
            model_name='keyresult',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Черновик'),
                    ('on_track', 'В графике'),
                    ('at_risk', 'Под риском'),
                    ('completed', 'Завершён'),
                ],
                default='draft',
                max_length=32,
                verbose_name='Статус',
            ),
        ),
    ]
