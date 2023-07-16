# Generated by Django 4.1 on 2023-07-16 19:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("code_execution", "0004_testcase"),
    ]

    operations = [
        migrations.CreateModel(
            name="Submission",
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
                ("submission_id", models.CharField(max_length=120)),
                ("code", models.TextField(max_length=10000)),
                (
                    "language",
                    models.CharField(
                        choices=[
                            ("CPP", "CPP"),
                            ("JAVA", "JAVA"),
                            ("PYTHON", "PYTHON"),
                        ],
                        default="CPP",
                        max_length=100,
                    ),
                ),
                (
                    "verdict",
                    models.CharField(
                        choices=[
                            ("ACCEPTED", "ACCEPTED"),
                            ("WRONG ANSWER", "WRONG ANSWER"),
                            ("TIME LIMIT EXCEEDED", "TIME LIMIT EXCEEDED"),
                            ("COMPILATION ERROR", "COMPILATION ERROR"),
                            ("MEMORY LIMIT EXCEEDED", "MEMORY LIMIT EXCEEDED"),
                        ],
                        default="WRONG ANSWER",
                        max_length=100,
                    ),
                ),
                ("time", models.DateTimeField(auto_now_add=True)),
                (
                    "problem",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="code_execution.problem",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]