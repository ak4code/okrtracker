from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('okr', '0005_replace_keyresult_order_with_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='keyresult',
            name='progress',
        ),
    ]
