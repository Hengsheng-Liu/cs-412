# Generated by Django 5.1.3 on 2024-12-06 02:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rate_my_interviewer', '0011_unlock'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckIn',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Date', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rate_my_interviewer.rmiprofile')),
            ],
        ),
    ]
