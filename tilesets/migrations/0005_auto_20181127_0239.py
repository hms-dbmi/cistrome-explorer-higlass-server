# Generated by Django 2.0.9 on 2018-11-27 02:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import tilesets.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tilesets', '0004_auto_20181115_1744'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_viewed_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', models.TextField()),
                ('description', models.TextField(blank=True)),
                ('uuid', models.CharField(default=tilesets.models.decoded_slugid, max_length=100, unique=True)),
                ('private', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created',),
                'permissions': (('read', 'Read permission'), ('write', 'Modify tileset'), ('admin', 'Administrator priviliges')),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.TextField(unique=True)),
                ('description', models.TextField(blank=True, default='')),
                ('refs', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterModelOptions(
            name='tileset',
            options={'ordering': ('created',), 'permissions': (('read', 'Read permission'), ('write', 'Modify tileset'), ('admin', 'Administrator priviliges'))},
        ),
        migrations.AlterField(
            model_name='tileset',
            name='uuid',
            field=models.CharField(default=tilesets.models.decoded_slugid, max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='tileset',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tilesets.Project'),
        ),
        migrations.AddField(
            model_name='tileset',
            name='tags',
            field=models.ManyToManyField(blank=True, to='tilesets.Tag'),
        ),
    ]
