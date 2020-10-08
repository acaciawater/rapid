# Generated by Django 2.2.12 on 2020-10-08 12:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import rapid.models
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ogc', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='group')),
                ('order', models.SmallIntegerField(default=1, verbose_name='order')),
                ('open', models.BooleanField(default=False, verbose_name='open')),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('bbox', models.CharField(blank=True, max_length=100, null=True, verbose_name='extent')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Layer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.SmallIntegerField(default=1, verbose_name='order')),
                ('visible', models.BooleanField(default=True, verbose_name='visible')),
                ('format', models.CharField(default='image/png', max_length=50, verbose_name='format')),
                ('minzoom', models.SmallIntegerField(blank=True, null=True, verbose_name='minzoom')),
                ('maxzoom', models.SmallIntegerField(blank=True, null=True, verbose_name='maxzoom')),
                ('transparent', models.BooleanField(default=True, verbose_name='transparent')),
                ('opacity', models.DecimalField(decimal_places=1, default=1.0, max_digits=4, verbose_name='opacity')),
                ('use_extent', models.BooleanField(default=True, verbose_name='Use extent')),
                ('clickable', models.BooleanField(default=False, help_text='show popup with info when layer is clicked', verbose_name='clickable')),
                ('properties', models.CharField(blank=True, help_text='comma separated list of properties to display when layer is clicked', max_length=200, null=True, verbose_name='properties')),
                ('allow_download', models.BooleanField(default=False, help_text='user can download this layer', verbose_name='downloadable')),
                ('stylesheet', models.URLField(blank=True, help_text='url of stylesheet for GetFeatureInfo response', null=True, verbose_name='stylesheet')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rapid.Group', verbose_name='group')),
                ('layer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ogc.Layer')),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rapid.Map', verbose_name='map')),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='map',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rapid.Map'),
        ),
        migrations.CreateModel(
            name='DocumentGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('open', models.BooleanField(default=False)),
                ('order', models.PositiveSmallIntegerField(default=1)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='rapid.DocumentGroup')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cluster', models.CharField(blank=True, max_length=30, null=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('url', models.URLField(blank=True, null=True)),
                ('doc', sorl.thumbnail.fields.ImageField(blank=True, null=True, upload_to=rapid.models.upload_to_cluster)),
                ('order', models.PositiveSmallIntegerField(default=1)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rapid.DocumentGroup')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together={('name', 'map')},
        ),
    ]