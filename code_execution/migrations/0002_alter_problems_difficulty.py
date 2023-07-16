# Generated by Django 4.1 on 2023-07-16 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("code_execution", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="problems",
            name="difficulty",
            field=models.CharField(
                choices=[
                    ("Easy", "Easy"),
                    ("Medium", "Medium"),
                    ("Difficult", "Difficult"),
                ],
                default="Easy",
                max_length=50,
            ),
        ),
    ]
