# Generated by Django 3.2.20 on 2023-08-20 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('authentications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_customer',
            field=models.BooleanField(default=False, verbose_name='Customer'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='photo',
            field=models.ImageField(null=True, upload_to='media'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='address',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='customuser_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_staff',
            field=models.BooleanField(default=False, verbose_name='Staff'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='customuser_permissions_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
