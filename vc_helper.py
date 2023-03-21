import requests
import os
import sys

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
    'lib/InsertaCodi.class',
    'lib/InsertaCodi.java',
    'lib/duplicate.sh',
    'lib/duplicatePython.sh',
    'lib/public/InsertaCodi.class',
    'lib/public/validators/customValidation.py',
    'scripts/build.sh',
    'scripts/grade.sh',
    'scripts/run.sh',
    'scripts/submit.sh',
    'starter_code/exercise.py',
    'work/exercise.py'
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
    Liss all the courses available to the user identified by the token
    """
    url = URL
    r = requests.get(url, headers=AUTH)
    for course in r.json()['courses']:
        print(f'{course["id"]:10} {course["name"]}')

def extract(course_id, target):
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
                    print(f'      {file} NOT FOUND')


if __name__ == "__main__":
    if sys.argv[1] == '-l':
        list_courses()
    elif len(sys.argv) == 5 and sys.argv[1] == '-e' and sys.argv[3] == '-t':
        course_id = sys.argv[2]
        target_path = sys.argv[4]
        extract(course_id, target_path)
    else:
        print("Usage: python vc_helper.py -l | -e <course_id> -t <target_path>")
        sys.exit(1)