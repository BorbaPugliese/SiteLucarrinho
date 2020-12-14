# Generated by Django 2.2.14 on 2020-12-14 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20201213_1706'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='stripe_customer_id',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='telefone',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]