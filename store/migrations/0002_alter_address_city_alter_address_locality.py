# Generated by Django 4.1.7 on 2023-03-02 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="city",
            field=models.CharField(max_length=150, verbose_name="Line 2"),
        ),
        migrations.AlterField(
            model_name="address",
            name="locality",
            field=models.CharField(max_length=150, verbose_name="Line 1"),
        ),
    ]
