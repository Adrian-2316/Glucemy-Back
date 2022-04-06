# Generated by Django 4.0.3 on 2022-04-06 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Foods',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('usual_measure', models.FloatField(default=0)),
                ('hc_rations', models.FloatField(default=0)),
                ('glycemic_index', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
