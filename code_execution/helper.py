import subprocess
import os


def get_extension(language):
    if language == "CPP":
        return ".cpp"
    elif language == "PYTHON":
        return ".py"
    elif language == "C":
        return ".c"
    elif language == "JAVA":
        return ".java"


def compiler_details(language, submission_id):
    extension = get_extension(language)
    compiler_dictionary = {"extension": extension, "language": language, "submission_id": submission_id}
    if language == "CPP":
        compiler_dictionary["compile"] = f"g++ -o {submission_id} {submission_id}.{extension}"
        compiler_dictionary["remove"] = f"{submission_id} {submission_id}.{extension}"
        compiler_dictionary["execute"] = f"./{submission_id}"
    elif language == "JAVA":
        compiler_dictionary["compile"] = f"g++ -o {submission_id} {submission_id}.{extension}"
        compiler_dictionary["remove"] = f"{submission_id} {submission_id}.{extension}"
        compiler_dictionary["execute"] = f"./{submission_id}"
    elif language == "PYTHON":
        compiler_dictionary["compile"] = f"python {submission_id}.{extension}"
        compiler_dictionary["remove"] = f"{submission_id}.{extension}"
        compiler_dictionary["execute"] = f"python {submission_id}.{extension}"
    elif language == "C":
        compiler_dictionary["compile"] = f"gcc -o {submission_id} {submission_id}.{extension}"
        compiler_dictionary["remove"] = f"{submission_id} {submission_id}.{extension}"
        compiler_dictionary["execute"] = f"./{submission_id}"
    return compiler_dictionary


def docker_init(compiler_dictionary, code_folder_path):
    image = "gcc"
    container = "cpp_container"
    if compiler_dictionary["language"] == "CPP":
        image = "gcc"
        container = "cpp_container"
    elif compiler_dictionary["language"] == "JAVA":
        image = "java"
        container = "java_container"
    elif compiler_dictionary["language"] == "PYTHON":
        image = "python"
        container = "python_container"
    elif compiler_dictionary["language"] == "C":
        image = "gcc"
        container = "c_container"
    # create a container
    subprocess.run(f"docker run --name {container} -dt {image}", shell=True)

    # copy the program files into the docker container
    subprocess.run(
        f"docker cp {code_folder_path}/{compiler_dictionary['submission_id']}.{compiler_dictionary['extension']} {container}:/{compiler_dictionary['submission_id']}.{compiler_dictionary['extension']}",
        shell=True)
    compiler_dictionary['container'] = container
    compiler_dictionary['image'] = image
    return compiler_dictionary


def create_testcase_file(testcase_folder_path, testcase, compiler_dictionary, testcase_number):
    if not os.path.exists(testcase_folder_path):
        os.makedirs(testcase_folder_path)
    file_path = testcase_folder_path + f"/{compiler_dictionary['submission_id']}{testcase_number}.txt"
    compiler_dictionary['testcase_name'] = f"/{compiler_dictionary['submission_id']}{testcase_number}.txt"
    with open(file_path, "w") as fp:
        fp.write(testcase)
    # now copy the testcase file to the docker container:
    subprocess.run(
        f"docker cp {file_path} {compiler_dictionary['container']}:/{compiler_dictionary['testcase_name']}",
        shell=True)
    # after copying delete the current testcase file created
    # subprocess.run(f"rm {file_path}", shell=True)
    return compiler_dictionary


def delete_docker_container(compiler_dictionary):
    # stop the running container
    subprocess.run(f"docker stop {compiler_dictionary['container']}", shell=True)
    # delete the container
    subprocess.run(f"docker rm {compiler_dictionary['container']}", shell=True)
