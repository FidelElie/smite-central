# Generated by Django 3.0.8 on 2020-07-15 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esports', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league', models.CharField(choices=[('SWC', 'Smite World Championship'), ('SPL', 'Smite Pro League')], default='SPL', max_length=3)),
                ('season', models.IntegerField()),
                ('playlist_id', models.CharField(max_length=50)),
            ],
        ),
    ]
