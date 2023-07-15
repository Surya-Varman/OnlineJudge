from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.




def execute_code(request):
    if(request.method == "POST"):
        pass
    return render(request, "code_execution/submit.html")
