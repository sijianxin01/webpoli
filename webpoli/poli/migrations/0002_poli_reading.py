# Generated by Django 4.1 on 2022-11-01 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poli', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='poli',
            name='reading',
            field=models.IntegerField(default=0, verbose_name='阅读量'),
        ),
    ]