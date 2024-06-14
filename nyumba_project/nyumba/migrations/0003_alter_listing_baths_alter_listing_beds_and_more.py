# Generated by Django 5.0.4 on 2024-06-14 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nyumba', '0002_listing_alter_profile_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='baths',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='beds',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='listing',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]
