# Generated by Django 2.0.4 on 2018-05-08 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csv_app', '0003_auto_20180508_1841'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='slug',
            field=models.CharField(default='None', max_length=20),
        ),
    ]
