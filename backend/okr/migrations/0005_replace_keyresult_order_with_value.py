from decimal import Decimal

from django.db import migrations, models

import okr.services.validators


def copy_order_to_value(apps, schema_editor):
    KeyResult = apps.get_model('okr', 'KeyResult')

    for key_result in KeyResult.objects.only('id', 'order').iterator():
        if key_result.order == 1:
            value = Decimal('0.3')
        elif key_result.order == 2:
            value = Decimal('0.7')
        else:
            value = Decimal('1.0')

        KeyResult.objects.filter(id=key_result.id).update(value=value)


class Migration(migrations.Migration):

    dependencies = [
        ('okr', '0004_alter_progress_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyresult',
            name='value',
            field=models.DecimalField(
                decimal_places=1,
                default=Decimal('0.3'),
                max_digits=2,
                verbose_name='Значение KR',
            ),
            preserve_default=False,
        ),
        migrations.RunPython(copy_order_to_value, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name='keyresult',
            name='unique_key_result_order_per_okr',
        ),
        migrations.RemoveField(
            model_name='keyresult',
            name='order',
        ),
        migrations.AlterField(
            model_name='keyresult',
            name='value',
            field=models.DecimalField(
                decimal_places=1,
                default=Decimal('0.3'),
                max_digits=2,
                validators=[okr.services.validators.validate_key_result_value],
                verbose_name='Значение KR',
            ),
        ),
    ]
