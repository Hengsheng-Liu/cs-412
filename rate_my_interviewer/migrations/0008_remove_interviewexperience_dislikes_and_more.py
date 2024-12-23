# Generated by Django 5.1.1 on 2024-12-01 22:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rate_my_interviewer', '0007_interviewexperience_dislikes_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interviewexperience',
            name='dislikes',
        ),
        migrations.RemoveField(
            model_name='interviewexperience',
            name='likes',
        ),
        migrations.CreateModel(
            name='Dislikes',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('experience', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rate_my_interviewer.interviewexperience')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rate_my_interviewer.rmiprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('experience', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rate_my_interviewer.interviewexperience')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rate_my_interviewer.rmiprofile')),
            ],
        ),
    ]
