import json

from celery import shared_task
import time
import os
import subprocess
import uuid
import json

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from code_execution.models import Problem as Problems, TestCase, Submission
from .helper import compiler_details, get_extension, docker_init, create_testcase_file, \
    delete_docker_container
from django.contrib.auth.models import User
FOLDER_PATH = os.getcwd() + "/codeFiles"
OLD_PATH = os.getcwd()
TESTCASE_PATH = os.getcwd() + "/testcases"


@shared_task(bind=True)
def test_func(self):
    return "Done"


@shared_task(bind=True)
def execute_code_celery(self, request):
    if not Problems.objects.filter(problem_id=request["POST"]["problem_id"]).exists():
        return "Problem Id does not exists"
    submission = Submission()
    submission.submission_id = uuid.uuid4()
    while Submission.objects.filter(submission_id=submission.submission_id).exists():
        submission.submission_id = uuid.uuid4()
    # submission.user = request.user
    submission.user = User.objects.get(username=request["user"])
    submission.problem = Problems.objects.get(problem_id=request["POST"]["problem_id"])
    submission.code = request["POST"]["code"]
    submission.language = request["POST"]["language"]
    extension = get_extension(submission.language)
    file_path = FOLDER_PATH + f"/{submission.submission_id}.{extension}"
    with open(file_path, "w") as file:
        file.write(submission.code)
    # os.chdir(FOLDER_PATH)
    compiler_dictionary = compiler_details(submission.language, submission.submission_id)
    compiler_dictionary = docker_init(compiler_dictionary, FOLDER_PATH)
    if compiler_dictionary['language'] != "PYTHON":
        output = subprocess.run(f"docker exec {compiler_dictionary['container']} {compiler_dictionary['compile']}",
                                shell=True)
    else:
        output = 0

    if compiler_dictionary['language'] != "PYTHON" and output.returncode != 0:
        submission.verdict = "COMPILATION ERROR"
        submission.save()
        delete_docker_container(compiler_dictionary)
        return "COMPILATION ERROR"
    else:
        testcases = TestCase.objects.filter(problem_id__problem_id=submission.problem.problem_id)
        for testcase_no, testcase in enumerate(testcases):
            compiler_dictionary = create_testcase_file(TESTCASE_PATH, testcase.testcase, compiler_dictionary,
                                                       testcase_no)
            try:
                command = [
                    "docker", "exec", compiler_dictionary['container'],
                    "sh", "-c", f"{compiler_dictionary['execute']} < {compiler_dictionary['testcase_name']}"
                ]
                code_output = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=2
                )
            except subprocess.TimeoutExpired:
                submission.verdict = "TIME LIMIT EXCEEDED"
                submission.save()
                delete_docker_container(compiler_dictionary)
                return "TIME LIMIT EXCEEDED"
            code_output = str(code_output.stdout)
            ts_output = testcase.output.replace('\r\n', '\n')
            if ts_output.strip() != code_output.strip():
                submission.verdict = "WRONG ANSWER"
                submission.save()
                delete_docker_container(compiler_dictionary)
                return f"WRONG ANSWER: EXPECTED: {ts_output.strip()} RECEIVED: {code_output.strip()}"

        submission.verdict = "ACCEPTED"
        submission.save()
        delete_docker_container(compiler_dictionary)
        return "ACCEPTED"

#
#
# def execute_code_celery(self, request):
#     if request.method == "POST":
#         if not Problems.objects.filter(problem_id=request.POST["problem_id"]).exists():
#             return HttpResponse("Problem Id does not exists")
#
#         submission = Submission()
#         submission.submission_id = uuid.uuid4()
#         while Submission.objects.filter(submission_id=submission.submission_id).exists():
#             submission.submission_id = uuid.uuid4()
#         submission.user = request.user
#         submission.problem = Problems.objects.get(problem_id=request.POST["problem_id"])
#         submission.code = request.POST["code"]
#         submission.language = request.POST["language"]
#         extension = get_extension(submission.language)
#         file_path = FOLDER_PATH + f"/{submission.submission_id}.{extension}"
#         with open(file_path, "w") as file:
#             file.write(submission.code)
#         # os.chdir(FOLDER_PATH)
#         compiler_dictionary = compiler_details(submission.language, submission.submission_id)
#         compiler_dictionary = docker_init(compiler_dictionary, FOLDER_PATH)
#
#         if compiler_dictionary['language'] != "PYTHON":
#             output = subprocess.run(f"docker exec {compiler_dictionary['container']} {compiler_dictionary['compile']}",
#                                     shell=True)
#         else:
#             output = 0
#
#         if compiler_dictionary['language'] != "PYTHON" and output.returncode != 0:
#             submission.verdict = "COMPILATION ERROR"
#             submission.save()
#             delete_docker_container(compiler_dictionary)
#             return HttpResponse("COMPILATION ERROR")
#         else:
#             testcases = TestCase.objects.filter(problem_id__problem_id=submission.problem.problem_id)
#             for testcase_no, testcase in enumerate(testcases):
#                 compiler_dictionary = create_testcase_file(TESTCASE_PATH, testcase.testcase, compiler_dictionary,
#                                                            testcase_no)
#                 try:
#                     command = [
#                         "docker", "exec", compiler_dictionary['container'],
#                         "sh", "-c", f"{compiler_dictionary['execute']} < {compiler_dictionary['testcase_name']}"
#                     ]
#                     code_output = subprocess.run(
#                         command,
#                         capture_output=True,
#                         text=True,
#                         timeout=2
#                     )
#                 except subprocess.TimeoutExpired:
#                     submission.verdict = "TIME LIMIT EXCEEDED"
#                     submission.save()
#                     delete_docker_container(compiler_dictionary)
#                     return HttpResponse("TIME LIMIT EXCEEDED")
#                 code_output = str(code_output.stdout)
#                 ts_output = testcase.output.replace('\r\n', '\n')
#                 if ts_output.strip() != code_output.strip():
#                     submission.verdict = "WRONG ANSWER"
#                     submission.save()
#                     delete_docker_container(compiler_dictionary)
#                     return HttpResponse(
#                         f"WRONG ANSWER: EXPECTED: {ts_output.strip()} RECEIVED: {code_output.strip()}")
#
#             submission.verdict = "ACCEPTED"
#             submission.save()
#             delete_docker_container(compiler_dictionary)
#             return HttpResponse("ACCEPTED")
#     else:
#         return render(request, "code_execution/submit.html")
