# Generated by Django 5.1.6 on 2025-03-27 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_teacher_groups_teacher_is_active_teacher_is_staff_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='last_login',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
