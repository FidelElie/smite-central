# Generated by Django 3.0.8 on 2020-07-31 10:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('esports', '0006_match_date_published'),
    ]

    operations = [
        migrations.AddField(
            model_name='highlight',
            name='match',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='esports.Match'),
        ),
    ]
