from django.contrib import admin
from code_execution.models import Problem, TestCase, Submission
admin.site.register(Problem)
admin.site.register(TestCase)
admin.site.register(Submission)
# Register your models here.
