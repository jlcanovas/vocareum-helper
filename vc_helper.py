import requests
import os
import sys
import json
import glob
from zipfile import ZipFile
import base64

# The script looks for the TOKEN file in the current directory
# The file must include the token from vocareum in the first line
TOKEN=open("TOKEN", "r").readline().strip()

# The main entry point to Vocareum API
URL = 'https://api.vocareum.com/api/v2/courses'
# The main header configuration
AUTH = {'Authorization': 'Token ' + TOKEN, 'Content-type': 'application/json'}

# Files to recover from each assignment part
FILES = [
    'asnlib/public/docs/README.html',
    'asnlib/public/test.py',
    'asnlib/public/validator.py',
    #'lib/InsertaCodi.class', # The API does not seem to give access to this file
    #'lib/InsertaCodi.java',
    #'lib/duplicate.sh',
    #'lib/duplicatePython.sh',
    #'lib/public/InsertaCodi.class',
    #'lib/public/validators/customValidation.py',
    'scripts/build.sh',
    'scripts/grade.sh',
    'scripts/run.sh',
    'scripts/submit.sh',
    'starter_code/exercise.py',
    #'work/exercise.py' # The API does not seem to give access to this file
]

def sanitize_str(str):
    """
    Sanitize a string to be used as a folder name
    Some names include the character "/" which causes conflicts. This character
    is replaced by #
    """
    return str.replace("/", "#").strip()

def list_courses():
    """
    Lits all the courses available to the user identified by the token
    """
    url = URL
    r = requests.get(url, headers=AUTH)
    for course in r.json()['courses']:
        print(f'{course["id"]:10} {course["name"]}')

def download(course_id, target):
    """
    Extract the files defined in FILES from the course identified by course_id
    to the target folder. The target folder will follow the same structure as
    the course in Vocareum. That is:

    target/course_name/assignment_name/part_name/file

    param course_id: The course identifier
    param target: The target folder
    """
    url = URL + "/" + course_id
    r_course = requests.get(url, headers=AUTH)
    course_name = r_course.json()['courses'][0]['name']
    print(f'Extracting {course_id} {course_name} to {target}')

    url = URL + "/" + course_id + '/assignments'
    r_assignments = requests.get(url, headers=AUTH)
    while len(r_assignments.json()['assignments']) > 0:
        for assigment in r_assignments.json()['assignments']:
            assignment_id = assigment['id']
            assignment_name = assigment['name']
            print(f'Found assignment {assignment_id} {assignment_name}')

            url_part = f'{URL}/{course_id}/assignments/{assignment_id}/parts'
            r_parts = requests.get(url_part, headers=AUTH)
            for part in r_parts.json()["parts"]:
                part_id = part['id']
                part_name = part['name']
                print(f'   Found part {part_id} {part_name}')

                for file in FILES:
                    url_file = f'{URL}/{course_id}/assignments/{assignment_id}/parts/{part_id}/files?filename={file}'
                    r_file = requests.get(url_file, headers=AUTH)
                    if 'files' in r_file.json() and len(r_file.json()['files']) > 0 and r_file.json()['files'][0]['filename'] == file and "does not exist" not in r_file.json()['files'][0]["download_url"]:
                        url_download = r_file.json()['files'][0]['download_url']
                        r_download = requests.get(url_download, allow_redirects=True)
                        target_path = f'{target}/{course_name}/{sanitize_str(assignment_name)}/{sanitize_str(part_name)}/{file}'
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        open(target_path, 'wb').write(r_download.content)
                        print(f'      {file} found and copied')
                    else:
                        sub_path = '/'.join(file.split('/')[:-1])
                        target_path = f'{target}/{course_name}/{sanitize_str(assignment_name)}/{sanitize_str(part_name)}/{sub_path}'
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        print(f'      {file} NOT FOUND')
        page += 1
        url = URL + "/" + course_id + '/assignments' + '?page=' + str(page)
        r_assignments = requests.get(url, headers=AUTH)

def zip_and_encode_folder(folder):
    """
    Prepares a zip file with the content of the folder and returns the base64
    """
    files = glob.glob(folder + "/**", recursive=True)
    files = [f for f in files if os.path.isfile(f)]
    files_zip = [f[len(folder)+1:] for f in files]
    with ZipFile("tmp.zip", "w") as zipfile:
        for file, file_zip in zip(files, files_zip):
            zipfile.write(file, file_zip)
    with open("tmp.zip", "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

def upload(course_id, assignment_id, part_id, target, source):    
    """
    Given a course, an assignment and a part, uploads the content of the source folder to target folder
    """
    data = {}
    data['update'] = 1 # 0 (default) | 1 - update the part (i.e., release the code to students )
    content_dict = {}
    content_dict['target'] = target
    content_dict['zipcontent'] = zip_and_encode_folder(source)
    data['content'] = [content_dict]
    url = f'{URL}/{course_id}/assignments/{assignment_id}/parts/{part_id}'
    data_string = json.dumps(data, indent = 4)
    r_put = requests.put(url, data = data_string, headers=AUTH)
    print(r_put.json())


if __name__ == "__main__":
    print(sys.argv, len(sys.argv))
    if sys.argv[1] == '-l':
        list_courses()
    elif len(sys.argv) == 5 and sys.argv[1] == '-d' and sys.argv[3] == '-t':
        course_id = sys.argv[2]
        target_path = sys.argv[4]
        download(course_id, target_path)
    elif len(sys.argv) == 11 and sys.argv[1] == '-u' and sys.argv[3] == '-a' and sys.argv[5] == '-p' and sys.argv[7] == '-t' and sys.argv[9] == '-s':
        course_id = sys.argv[2]
        assignment_id = sys.argv[4]
        part_id = sys.argv[6]
        target_folder = sys.argv[8]
        source_folder = sys.argv[10]
        upload(course_id, assignment_id, part_id, target_folder, source_folder)
    else:
        print("Usage: python vc_helper.py -l")
        print("       python vc_helper.py -d <course_id> -t <target_path>")
        print("       python vc_helper.py -u <course_id> -a <assignment_id> -p <part_id> -t <target_folder> -s <source_folder>")
        sys.exit(1)