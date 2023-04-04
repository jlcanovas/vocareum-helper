import requests
import os
import sys
import json
import glob
from zipfile import ZipFile
import base64
import time
from datetime import datetime  

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

# Delay between requests to avoid getting an error by the API
DELAY=15

# Default target folder
TARGET_FOLDER='data'

# Defaulf config file name
CONFIG_FILE='config.json'

def sanitize_str(str):
    """
    Sanitize a string to be used as a folder name
    Some names include the character "/" which causes conflicts. This character
    is replaced by #
    """
    return str.replace("/", "#").strip()

def list():
    """
    Lits all the courses available to the user identified by the token
    """
    url = URL
    r = requests.get(url, headers=AUTH)
    print(f'Courses found with the provided token:')
    print(f'{"COURSE_ID":10} COURSE_NAME')
    for course in r.json()['courses']:
        print(f'{course["id"]:10} {course["name"]}')

def init(course_id, selected_assignments=None):
    """
    Init the target folder with the content of the course identified by course_id. 
    The target folder will follow the same structure as the course in Vocareum, 
    that is: 
    
    TARGET_FOLDER/course_name/assignment_name/part_name/file
    TARGET_FOLDER is a global variable defined in this file

    The function will also create the file "config.json" in the target folder.
    This file will include basic information about the course, assignmentes and
    parts. DO NOT REMOVE THIS FILE.

    param course_id: The course identifier
    param selected_assignments: List of assignment ids to be downloaded. If None, all
    """
    # Getting the course name 
    r_course = requests.get(f'{URL}/{course_id}', headers=AUTH)
    course_name = r_course.json()['courses'][0]['name']
    print(f'Initializing {TARGET_FOLDER} with course id:{course_id} name:{course_name}')
    config = { "course_name": course_name, 
               "course_id": course_id, 
               "assignments": [], 
               "timestamp": str(datetime.fromtimestamp(datetime.now().timestamp())) }

    # Getting the assignments (using pagination)
    page = 0
    r_assignments = requests.get(f'{URL}/{course_id}/assignments?page={page}', headers=AUTH)
    while len(r_assignments.json()['assignments']) > 0:
        for assigment in r_assignments.json()['assignments']:
            assignment_config = { "assignment_id": assigment['id'], "assignment_name": assigment['name'], "parts": [], "timestamp": str(datetime.fromtimestamp(datetime.now().timestamp())) }

            # Checking if assignment name matches the filter (if any)
            if selected_assignments is not None and assignment_config["assignment_id"] not in selected_assignments:
                print(f'  Found assignment {assignment_config["assignment_id"]} {assignment_config["assignment_name"]}. Skipping...')
                continue
                
            print(f'  Found assignment {assignment_config["assignment_id"]} {assignment_config["assignment_name"]}')
            r_parts = requests.get(f'{URL}/{course_id}/assignments/{assignment_config["assignment_id"]}/parts', headers=AUTH)
            for part in r_parts.json()["parts"]:
                part_config = { "part_id": part['id'], "part_name": part['name'], "files": [] }
                print(f'    Found part {part_config["part_id"]} {part_config["part_name"]}')

                for file in FILES:
                    remote_path = f'{URL}/{course_id}/assignments/{assignment_config["assignment_id"]}/parts/{part_config["part_id"]}/files?filename={file}'
                    r_file = requests.get(remote_path, headers=AUTH)
                    # All these conditions are here to check that we are actually getting the files (no error, no other file, etc.)
                    if 'files' in r_file.json() and len(r_file.json()['files']) > 0 and r_file.json()['files'][0]['filename'] == file and "does not exist" not in r_file.json()['files'][0]["download_url"]:
                        url_download = r_file.json()['files'][0]['download_url']
                        r_download = requests.get(url_download, allow_redirects=True)
                        local_path = f'{TARGET_FOLDER}/{course_name}/{sanitize_str(assignment_config["assignment_name"])}/{sanitize_str(part_config["part_name"])}/{file}'
                        os.makedirs(os.path.dirname(local_path), exist_ok=True)
                        open(local_path, 'wb').write(r_download.content)
                        print(f'      {file} found and copied')
                        part_config["files"].append({"reference_path": file, "remote_path" : remote_path, "local_path" : local_path})
                    else:
                        # If the file is not found, we create the folder structure anyway
                        sub_path = '/'.join(file.split('/')[:-1])
                        local_path = f'{TARGET_FOLDER}/{course_name}/{sanitize_str(assignment_config["assignment_name"])}/{sanitize_str(part_config["part_name"])}/{sub_path}'
                        os.makedirs(os.path.dirname(local_path), exist_ok=True)
                        print(f'      {file} NOT FOUND')
                assignment_config["parts"].append(part_config)
            config["assignments"].append(assignment_config)

        page += 1 # Next page!
        r_assignments = requests.get(f'{URL}/{course_id}/assignments?page={page}', headers=AUTH)
    
    with open(f'{TARGET_FOLDER}/{CONFIG_FILE}', "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def download(selected_assignments=None):
    """
    You must call init() before calling this function.

    Uses the information in the file "config.json" to refresh the files downloaded
    during the init process. 

    param selected_assignments: List of assignment ids to be downloaded. If None, all
    """
    # Remember: init() first!
    if not os.path.exists(f'{TARGET_FOLDER}/{CONFIG_FILE}'):
        print("ERROR: config.json not found. Please call init() first")

    # Getting the configuration
    config = {}
    with open(f'{TARGET_FOLDER}/{CONFIG_FILE}', "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # We follow the config file to download the files
    print(f'Downloading files for course {config["course_name"]}')
    for assignment in config["assignments"]:

        # Checking if assignment name matches the filter (if any)
        if selected_assignments is not None and assignment["assignment_id"] not in selected_assignments:
            print(f'  Assignment {assignment["assignment_id"]} {assignment["assignment_name"]}. Skipping...')
            continue

        print(f'  Assignment {assignment["assignment_id"]} {assignment["assignment_name"]}')
        for part in assignment["parts"]:
            print(f'    Part {part["part_id"]} {part["part_name"]}')
            for file in part["files"]:
                remote_path = file["remote_path"]
                r_file = requests.get(remote_path, headers=AUTH)
                if 'files' in r_file.json() and len(r_file.json()['files']) > 0 and r_file.json()['files'][0]['filename'] == file["reference_path"] and "does not exist" not in r_file.json()['files'][0]["download_url"]:
                    url_download = r_file.json()['files'][0]['download_url']
                    r_download = requests.get(url_download, allow_redirects=True)
                    local_path = file["local_path"]
                    open(local_path, 'wb').write(r_download.content)
                    print(f'      {file["reference_path"]} refreshed')
                else:
                    print(f'      {file["reference_path"]} NOT FOUND')
        assignment["timestamp"] = str(datetime.fromtimestamp(datetime.now().timestamp()))
    
    with open(f'{TARGET_FOLDER}/{CONFIG_FILE}', "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


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


def upload_part(course_id, assignment_id, part_id, target, source):    
    """
    Given a course, an assignment and a part, uploads the content of the source folder to target folder
    """
    data = {}
    data['update'] = 1 # 0 (default) | 1 - update the part (i.e., release the code to students )
    content_dict = {}
    content_dict['target'] = target # asnlib / scripts / lib / startercode
    content_dict['zipcontent'] = zip_and_encode_folder(source)
    data['content'] = [content_dict]
    url = f'{URL}/{course_id}/assignments/{assignment_id}/parts/{part_id}'
    data_string = json.dumps(data, indent = 4)
    r_put = requests.put(url, data = data_string, headers=AUTH)
    return r_put


def upload(selected_assignments=None):
    """
    You must call init() before calling this function.

    Uses the information in the file "config.json" to upload the files downloaded
    during the init process. 

    As the Vocareum API only supports uploading set of vias (as zip file) for a
    specific fodler in a part, this function will upload the files contained in the 
    folders of the downloaded files.

    param selected_assignments: List of assignment ids to be uploaded. If None, all
    """
    # Remember: init() first!
    if not os.path.exists(f'{TARGET_FOLDER}/config.json'):
        print("ERROR: config.json not found. Please call init() first")

    # Getting the configuration
    config = {}
    with open(f'{TARGET_FOLDER}/config.json', "r", encoding="utf-8") as f:
        config = json.load(f)

    # We follow the config file to upload the files
    # Unlike download, we focus on the folder (and not upload file by file)
    print(f'Uploading files for course {config["course_name"]}')
    for assignment in config["assignments"]:

        # Checking if assignment name matches the filter (if any)
        if selected_assignments is not None and assignment["assignment_id"] not in selected_assignments:
            print(f'  Assignment {assignment["assignment_id"]} {assignment["assignment_name"]}. Skipping...')
            continue

        print(f'  Assignment {assignment["assignment_id"]} {assignment["assignment_name"]}')

        for part in assignment["parts"]:
            print(f'    Part {part["part_id"]} {part["part_name"]}')
            
            folders = [] # we control the folders already uploaded
            for file in part["files"]:
                # Getting the main first folder (e.g., asnlib, scripts, etc.)
                reference_folder = file["reference_path"].split("/")[0] 

                # If already uploaded, skip!
                if reference_folder in folders:
                    continue
                    
                # Uploading the folder...
                local_folder = f'{file["local_path"].split(file["reference_path"])[0]}{reference_folder}'
                upload_result = upload_part(config["course_id"], assignment["assignment_id"], part["part_id"], reference_folder, local_folder)

                # Checking the results and printing the status
                if "status" in upload_result.json() and upload_result.json()['status'] == 'success':
                    print(f'      Folder {local_folder} uploaded')
                elif "error" in upload_result.json():
                    print(f'      Error uploading {local_folder}')
                    print('ERROR: ', upload_result.json()['error']['message'])
                else:
                    print(f'      Error uploading {local_folder}')
                    print('UNKNOWN ERROR')

                folders.append(reference_folder) if reference_folder not in folders else None

                # This is cumbersome... delay to avoid getting an error the server
                time.sleep(DELAY) 
                    
                           
if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'list':
        list()
    elif len(sys.argv) == 3 and sys.argv[1] == 'init':
        course_id = sys.argv[2]
        init(course_id)
    elif len(sys.argv) >= 4 and sys.argv[1] == 'init-filter':
        course_id = sys.argv[2]
        assigment_list = sys.argv[3:]
        init(course_id, assigment_list)
    elif len(sys.argv) == 2 and sys.argv[1] == 'download':
        download()
    elif len(sys.argv) == 3 and sys.argv[1] == 'download-filter':
        assigment_list = sys.argv[2:]
        download(assigment_list)
    elif len(sys.argv) == 2 and sys.argv[1] == 'upload':
        upload()
    elif len(sys.argv) == 3 and sys.argv[1] == 'upload-filter':
        assigment_list = sys.argv[2:]
        upload(assigment_list)
    else:
        print("Usage:")
        print("  python vc list")
        print("  python vc init <course_id>")
        print("  python vc download")
        print("  python vc upload")
        print("  python vc init-filter <course_id> <assignment_1> <assignment_2> ...")
        print("  python vc download-filter <assignment_1> <assignment_2> ...")
        print("  python vc upload-filter <assignment_1> <assignment_2> ...")
        sys.exit(1)