# Generated by Django 5.1.5 on 2025-05-12 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_audio_description_audio_featured_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audio',
            name='featured_image',
            field=models.ImageField(blank=True, default='featured_image/default.png', null=True, upload_to='featured_imge/'),
        ),
    ]
