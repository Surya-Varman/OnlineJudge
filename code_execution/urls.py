from django.urls import path
from . import views

urlpatterns = [
    path('', views.execute_code, name="execute"),
    path('submit_problem', views.submit_problem, name="submit_problem"),
    path('upload_testcase', views.upload_testcase, name="upload_testcase"),
]