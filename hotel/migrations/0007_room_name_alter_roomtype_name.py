# Generated by Django 4.2.2 on 2023-07-17 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0006_remove_roomtype_quntity_room_description_room_images_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='name',
            field=models.CharField(default='room name', max_length=100),
        ),
        migrations.AlterField(
            model_name='roomtype',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]