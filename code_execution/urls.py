from django.urls import path
from . import views

urlpatterns = [
    path('', views.execute_code, name="execute")
]