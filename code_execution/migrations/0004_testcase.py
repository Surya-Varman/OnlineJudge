# Generated by Django 4.1 on 2023-07-16 13:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("code_execution", "0003_rename_problems_problem"),
    ]

    operations = [
        migrations.CreateModel(
            name="TestCase",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("testcase_id", models.CharField(max_length=120)),
                ("testcase", models.TextField(max_length=10000)),
                ("output", models.TextField(max_length=10000)),
                (
                    "problem_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="code_execution.problem",
                    ),
                ),
            ],
        ),
    ]
