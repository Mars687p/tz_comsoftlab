# Generated by Django 5.1.1 on 2024-09-21 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imap_message', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='messagemodel',
            options={'ordering': ['-uid'], 'verbose_name': 'Письмо', 'verbose_name_plural': 'Письма'},
        ),
    ]
