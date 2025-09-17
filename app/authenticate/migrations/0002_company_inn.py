from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('authenticate', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='inn',
            field=models.CharField(default='0000000000', max_length=12, unique=True, verbose_name='ИНН'),
            preserve_default=False,
        ),
    ]