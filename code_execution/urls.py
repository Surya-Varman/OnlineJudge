from django.urls import path
from . import views

urlpatterns = [
    path('execute', views.execute_code, name="execute"),
    path('submit_problem', views.submit_problem, name="submit_problem"),
    path('upload_testcase', views.upload_testcase, name="upload_testcase"),
    path('problems/<str:problem_id>', views.view_problem, name="show_problem"),
    path('', views.show_problem, name="show_problems")
]