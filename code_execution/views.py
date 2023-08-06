from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from code_execution.models import Problem as Problems, TestCase, Submission
from code_execution.helper import compiler_details, get_extension, docker_init, create_testcase_file, \
    delete_docker_container
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .tasks import test_func, execute_code_celery
from django.core import serializers
from celery.result import AsyncResult

import os
import subprocess
import docker
import uuid
import timeit
import time

FOLDER_PATH = os.getcwd() + "/codeFiles"
OLD_PATH = os.getcwd()
TESTCASE_PATH = os.getcwd() + "/testcases"


@login_required(login_url="/users/login")
def execute_code(request):
    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)
    if request.method == "POST":
        data = {
            'POST': request.POST,
            'user': request.user.username,
        }
        res = execute_code_celery.delay(data)
        return_value = res.get()
        return HttpResponse(return_value)
    else:
        return render(request, "code_execution/submit.html")


    # if not os.path.exists(FOLDER_PATH):
    #     os.makedirs(FOLDER_PATH)
    # if request.method == "POST":
    #     if not Problems.objects.filter(problem_id=request.POST["problem_id"]).exists():
    #         return HttpResponse("Problem Id does not exists")
    #
    #     submission = Submission()
    #     submission.submission_id = uuid.uuid4()
    #     while Submission.objects.filter(submission_id=submission.submission_id).exists():
    #         submission.submission_id = uuid.uuid4()
    #     submission.user = request.user
    #     submission.problem = Problems.objects.get(problem_id=request.POST["problem_id"])
    #     submission.code = request.POST["code"]
    #     submission.language = request.POST["language"]
    #     extension = get_extension(submission.language)
    #     file_path = FOLDER_PATH + f"/{submission.submission_id}.{extension}"
    #     with open(file_path, "w") as file:
    #         file.write(submission.code)
    #     # os.chdir(FOLDER_PATH)
    #     compiler_dictionary = compiler_details(submission.language, submission.submission_id)
    #     compiler_dictionary = docker_init(compiler_dictionary, FOLDER_PATH)
    #
    #     if compiler_dictionary['language'] != "PYTHON":
    #         output = subprocess.run(f"docker exec {compiler_dictionary['container']} {compiler_dictionary['compile']}",
    #                                 shell=True)
    #     else:
    #         output = 0
    #
    #     if compiler_dictionary['language'] != "PYTHON" and output.returncode != 0:
    #         submission.verdict = "COMPILATION ERROR"
    #         submission.save()
    #         delete_docker_container(compiler_dictionary)
    #         return HttpResponse("COMPILATION ERROR")
    #     else:
    #         testcases = TestCase.objects.filter(problem_id__problem_id=submission.problem.problem_id)
    #         for testcase_no, testcase in enumerate(testcases):
    #             compiler_dictionary = create_testcase_file(TESTCASE_PATH, testcase.testcase, compiler_dictionary,
    #                                                        testcase_no)
    #             try:
    #                 command = [
    #                     "docker", "exec", compiler_dictionary['container'],
    #                     "sh", "-c", f"{compiler_dictionary['execute']} < {compiler_dictionary['testcase_name']}"
    #                 ]
    #                 code_output = subprocess.run(
    #                     command,
    #                     capture_output=True,
    #                     text=True,
    #                     timeout=2
    #                 )
    #             except subprocess.TimeoutExpired:
    #                 submission.verdict = "TIME LIMIT EXCEEDED"
    #                 submission.save()
    #                 delete_docker_container(compiler_dictionary)
    #                 return HttpResponse("TIME LIMIT EXCEEDED")
    #             code_output = str(code_output.stdout)
    #             ts_output = testcase.output.replace('\r\n', '\n')
    #             if ts_output.strip() != code_output.strip():
    #                 submission.verdict = "WRONG ANSWER"
    #                 submission.save()
    #                 delete_docker_container(compiler_dictionary)
    #                 return HttpResponse(
    #                     f"WRONG ANSWER: EXPECTED: {ts_output.strip()} RECEIVED: {code_output.strip()}")
    #
    #         submission.verdict = "ACCEPTED"
    #         submission.save()
    #         delete_docker_container(compiler_dictionary)
    #         return HttpResponse("ACCEPTED")
    # else:
    #     return render(request, "code_execution/submit.html")


def submit_problem(request):
    if request.method == "POST":
        problem = Problems()
        problem.problem_id = uuid.uuid4()
        while Problems.objects.filter(problem_id=problem.problem_id).exists():
            problem.problem_id = uuid.uuid4()
        problem.problem_title = request.POST["problem_title"]
        if Problems.objects.filter(problem_title=problem.problem_title):
            return HttpResponse("Problem title already exists choose another one")
        problem.problem_statement = request.POST["problem_statement"]
        problem.difficulty = request.POST["problem_difficulty"]
        problem.user_uploaded = request.user
        problem.save()
        return HttpResponse("Problem saved successfully!")
    else:
        return render(request, "code_execution/problem_upload.html")


def upload_testcase(request):
    if request.method == "POST":
        test_case = TestCase()
        test_case.testcase_id = uuid.uuid4()
        test_case.problem_id = Problems.objects.get(problem_id=request.POST["problem_id"])
        while TestCase.objects.filter(testcase_id=test_case.testcase_id).exists():
            test_case.testcase_id = uuid.uuid4()
        if not Problems.objects.filter(problem_id=request.POST["problem_id"]).exists():
            return HttpResponse("Entered problem does not exists")
        test_case.testcase = request.POST["testcase"]
        test_case.output = request.POST["output"]
        test_case.save()
        messages.success(request, 'Problem submitted successfully!')
        return HttpResponse("Testcase added successfully")
    else:
        return render(request, "code_execution/upload_testcases.html")


def show_problem(request):
    problems = Problems.objects.all()
    updated_problems = []
    for problem in problems:
        new_object = {'problem': problem}
        if Submission.objects.filter(Q(problem__problem_id=problem.problem_id) & Q(verdict="ACCEPTED") & Q(
                user__username=request.user.username)).exists():
            new_object['status'] = "Solved"
        elif Submission.objects.filter(
                Q(problem__problem_id=problem.problem_id) & Q(user__username=request.user.username)).exists():
            new_object['status'] = "Unsolved"
        else:
            new_object['status'] = "Unattempted"
        updated_problems.append((new_object))
    return render(request, "code_execution/problems.html", {"problems": updated_problems})


def view_problem(request, problem_id):
    problem = Problems.objects.get(problem_id=problem_id)
    return render(request, "code_execution/problem_description.html",
                  {"problem_title": problem.problem_title, "problem_description": problem.problem_statement,
                   "problem_id": problem_id})


def test_link(request):
    res = test_func.delay()
    print("State is: ", res.state)
    while res.state == 'PENDING':
        print(res.state)
    return HttpResponse("This is a test link")
