from django.db import models
from django.contrib.auth.models import User


class Problem(models.Model):
    difficulty_choices = [("Easy", "Easy"), ("Medium", "Medium"), ("Difficult", "Difficult")]
    problem_id = models.CharField(max_length=120)
    problem_title = models.CharField(max_length=200)
    problem_statement = models.TextField(max_length=10000)
    difficulty = models.CharField(max_length=50, choices=difficulty_choices, default="Easy")
    count_solved = models.IntegerField(default=0)
    count_attempted = models.IntegerField(default=0)
    user_uploaded = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class TestCase(models.Model):
    problem_id = models.ForeignKey(Problem, on_delete=models.CASCADE)
    testcase_id = models.CharField(max_length=120)
    testcase = models.TextField(max_length=10000)
    output = models.TextField(max_length=10000)


class Submission(models.Model):
    verdict_choices = [("ACCEPTED", "ACCEPTED"), ("WRONG ANSWER", "WRONG ANSWER"),
                       ("TIME LIMIT EXCEEDED", "TIME LIMIT EXCEEDED"), ("COMPILATION ERROR", "COMPILATION ERROR"),
                       ("MEMORY LIMIT EXCEEDED", "MEMORY LIMIT EXCEEDED")]
    language_choices = [("CPP", "CPP"), ("JAVA", "JAVA"), ("PYTHON", "PYTHON")]
    submission_id = models.CharField(max_length=120)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField(max_length=10000)
    language = models.CharField(max_length=100,choices = language_choices, default="CPP")
    verdict = models.CharField(max_length=100, choices=verdict_choices, default="WRONG ANSWER")
    time = models.DateTimeField(auto_now_add=True)
