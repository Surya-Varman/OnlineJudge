from django.shortcuts import render
from django.http import HttpResponse
import uuid
from code_execution.models import Problem as Problems, TestCase, Submission
from django.conf import settings

import os
import subprocess

FOLDER_PATH = os.getcwd() + "/codeFiles"
OLD_PATH = os.getcwd()

def execute_code(request):
    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)
    if request.method == "POST":
        if not Problems.objects.filter(problem_id=request.POST["problem_id"]).exists():
            return HttpResponse("Problem Id does not exists")
        submission = Submission()
        submission.submission_id = uuid.uuid4()
        while Submission.objects.filter(submission_id=submission.submission_id).exists():
            submission.submission_id = uuid.uuid4()
        submission.user = request.user
        # return HttpResponse(Problems.objects.get(request.POST["problem_id"]))
        submission.problem = Problems.objects.get(problem_id=request.POST["problem_id"])
        submission.code = request.POST["code"]
        submission.language = request.POST["language"]
        extension = ".cpp"
        if submission.language == "JAVA":
            extension = ".java"
        elif submission.language == "PYTHON":
            extension = ".py"
        file_path = FOLDER_PATH + f"/{submission.submission_id}.{extension}"
        with open(file_path, "w") as file:
            file.write(submission.code)
        os.chdir(FOLDER_PATH)
        compiler_dictionary = {"compile": "", "remove": "", "execute": ""}
        if submission.language == "CPP":
            compiler_dictionary["compile"] = f"g++ -o {submission.submission_id} {submission.submission_id}.{extension}"
            compiler_dictionary["remove"] = f"{submission.submission_id} {submission.submission_id}.{extension}"
            compiler_dictionary["execute"] = f".\{submission.submission_id}"
        elif submission.language == "JAVA":
            compiler_dictionary["compile"] = f"g++ -o {submission.submission_id} {submission.submission_id}.{extension}"
            compiler_dictionary["remove"] = f"{submission.submission_id} {submission.submission_id}.{extension}"
            compiler_dictionary["execute"] = f"./{submission.submission_id}"
        elif submission.language == "PYTHON":
            compiler_dictionary["compile"] = f"python {submission.submission_id} {submission.submission_id}.{extension}"
            compiler_dictionary["remove"] = f"{submission.submission_id}.{extension}"
            compiler_dictionary["execute"] = f"python {submission.submission_id}.{extension}"

        output = subprocess.run(compiler_dictionary["compile"], shell=True)
        if output.returncode != 0:
            submission.verdict = "COMPILATION ERROR"
            submission.save()
            return HttpResponse("COMPILATION ERROR")
        else:
            code_output = subprocess.run(compiler_dictionary["execute"], shell=True, capture_output=True, text=True)
            code_output = str(code_output.stdout)
            testcases = TestCase.objects.filter(problem_id__problem_id=submission.problem.problem_id)
            for testcase in testcases:
                if testcase.output.strip() != code_output.strip():
                    submission.verdict = "WRONG ANSWER"
                    submission.save()
                    return HttpResponse(f"WRONG ANSWER: EXPECTED: {testcase.output.strip()} RECEIVED: {code_output.strip()}")

            submission.verdict = "ACCEPTED"
            submission.save()
            return HttpResponse("ACCEPTED")
    else:
        return render(request, "code_execution/submit.html")


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
        return HttpResponse("Testcase added successfully")
    else:
        return render(request, "code_execution/upload_testcases.html")
