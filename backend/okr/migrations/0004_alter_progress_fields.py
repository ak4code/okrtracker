import django.core.validators
from decimal import Decimal

from django.db import migrations, models

import okr.services.validators


class Migration(migrations.Migration):
    dependencies = [
        ('okr', '0003_changelog_checkin_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keyresult',
            name='progress',
            field=models.DecimalField(
                decimal_places=1,
                default=Decimal('0.3'),
                max_digits=2,
                validators=[okr.services.validators.validate_key_result_progress],
                verbose_name='Прогресс',
            ),
        ),
        migrations.AlterField(
            model_name='okr',
            name='progress',
            field=models.DecimalField(
                decimal_places=1,
                default=0,
                max_digits=2,
                validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)],
                verbose_name='Прогресс',
            ),
        ),
    ]
