# Generated by Django 2.2.12 on 2020-10-08 12:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Layer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('layername', models.CharField(max_length=100, verbose_name='layername')),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('bbox', models.CharField(blank=True, max_length=100, null=True, verbose_name='extent')),
                ('attribution', models.CharField(blank=True, max_length=200, null=True, verbose_name='attribution')),
                ('tiled', models.BooleanField(default=True, verbose_name='tiled')),
                ('legend', models.URLField(blank=True, null=True, verbose_name='legend_url')),
            ],
            options={
                'verbose_name': 'Layer',
            },
        ),
        migrations.CreateModel(
            name='Legend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('property', models.CharField(max_length=40, verbose_name='property')),
                ('title', models.CharField(default='legend', max_length=40, verbose_name='title')),
                ('layer', models.ForeignKey(limit_choices_to={'server__service_type': 'WFS'}, on_delete=django.db.models.deletion.CASCADE, related_name='legends', to='ogc.Layer')),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
                ('url', models.URLField(max_length=255, verbose_name='url')),
                ('service_type', models.CharField(choices=[('WMS', 'WMS'), ('WFS', 'WFS')], default='WMS', max_length=4, verbose_name='type')),
                ('version', models.CharField(choices=[('WMS', (('1.1.1', '1.1.1'), ('1.3.0', '1.3.0'))), ('WFS', (('1.0.0', '1.0.0'), ('1.1.0', '1.1.0'), ('2.0.0', '2.0.0'), ('3.0.0', '3.0.0')))], default='1.3.0', max_length=10, verbose_name='version')),
            ],
            options={
                'verbose_name': 'Server',
            },
        ),
        migrations.CreateModel(
            name='Value',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=20)),
                ('label', models.CharField(blank=True, max_length=80, null=True)),
                ('value', models.CharField(max_length=40)),
                ('legend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ogc.Legend')),
            ],
            options={
                'ordering': ('value',),
            },
        ),
        migrations.CreateModel(
            name='Range',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=20)),
                ('label', models.CharField(blank=True, max_length=80, null=True)),
                ('lo', models.FloatField()),
                ('hi', models.FloatField()),
                ('legend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ogc.Legend')),
            ],
            options={
                'ordering': ('lo', 'hi'),
            },
        ),
        migrations.AddField(
            model_name='layer',
            name='server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ogc.Server', verbose_name='server'),
        ),
    ]
