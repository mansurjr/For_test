# Generated by Django 5.1.7 on 2025-04-03 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_alter_attendance_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='status',
            field=models.CharField(blank=True, choices=[('Present', 'Present'), ('Absent', 'Absent')], default='Absent', max_length=10, null=True),
        ),
    ]
