This repository a Python script to help you with the Vocareum platform via its REST API.

# Creating the access token

As the Vocareum REST API uses a token-based authentication, you need to create a token in your Vocareum account. You can create a token by going to your profile page, "Settings" option and "Personal Access Tokens" tab. 

Once you have created the token, you need to create a file called `TOKEN` in the root folder and paste the token in its first line.

# The script `vc.py`

This is the main script. The script currently has four main working modes: `list`, `init`, `download` and `upload`. 
We explain how to use each mode in the following.

## `list` mode

This option lists the available courses visible to the user (with the provided token). The output follows the pattern:

```
COURSE_ID COURSE_NAME
```

## `init` mode

This is the initialization mode and **must be called before using the `download` or `upload` modes**. 
In the initialization phase, the script will download the assignments, parts and files for a given course.
Furthermore, it will create a configuration file with the main information of the course resources. 
This configuration file is used by the `download` and `upload` modes to track the files to download or upload.

This mode receives the following parameters:
* `course_id` is the course ID to initialize. This parameter is mandatory.

For instance, the following command will execute the initialization for the course with ID `12345`:

```bash
python vc.py init 12345
```

This mode uses the following **default configuration**:
* `TARGET_FOLDER` is the folder where the files will be downloaded. By default, it is `./data`. 
Note that this file is already included in the `gitignore` file.
* `CONFIG_FILE` is the configuration file that will be created. By default, it is `./config.json`.
* The set of files that are downloaded are indicated in the `FILES` variable in the script, which currently cover the most important files (and others required in our courses) are:

  ```python
  FILES = [
      'asnlib/public/docs/README.html',
      'asnlib/public/test.py',
      'asnlib/public/validator.py',
      'scripts/build.sh',
      'scripts/grade.sh',
      'scripts/run.sh',
      'scripts/submit.sh',
      'startercode/exercise.py',
  ]
  ```

  > Note: files in the `lib` and `work` folder does not seem to be accessible via the REST API.

Optionally, this mode can be executed including a list of assignments to initialize, thus avoiding the initialization of all the assignments.
To do so, the command to use is `init-filter` followed by the course ID and the list of assignment identifiers to initialize.
For instance, the following command will initialize the assignments `223` and `112`:

```bash
python vc.py init-filter 12345 223 112
```

## `download` mode

This mode refreshes the files in the `TARGET_FOLDER` with the latest version in the Vocareum course.
It uses the configuration file created in the `init` mode to know which files to download.
Only the files indicated in such a file will be downloaded

For instance, the following command will download the files:

```bash
python vc.py download
```

As it is provided for the init mode, you can also perform a download for a subset of assignments. 
This is an example of command to download the assignments `223` and `112`:

```bash
python vc.py download-filter 223 112
```

## `upload` mode

This option uploads previously downloaded files. 
As the download mode, it relies on the information in the configuration file to know which files to upload.
However, due to the design of the Vocareum REST API, the files are uploaded according to the folders in the parts.

> Note: Due to restrictions in the Vocareum REST API, the upload process includes a delay of 15 seconds between uploads. This is to avoid the API to return an error.

As example, the following command will update the files:

```bash
python vc.py upload
```

As it is provided for the init mode, you can also perform an upload for a subset of assignments. 
This is an example of command to upload the assignments `223` and `112`:

```bash
python vc.py upload-filter 223 112
```

# Contributing

This project was just a quick side project to help me to deal with Vocareum interface, but if you want to contribute, any comment is welcome! If you are interested in contributing to this project, please read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

Just remember that:

1. Anyone participating will be subject to and agrees to sign on to the [Code of Conduct](CODE_OF_CONDUCT.md).

2. The development and community management of this project follows the governance rules described in the [GOVERNANCE.md](GOVERNANCE.md) document.

# License

This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>

The [CC BY-SA](https://creativecommons.org/licenses/by-sa/4.0/) license allows reusers to distribute, remix, adapt, and build upon the material in any medium or format, so long as attribution is given to the creator. The license allows for commercial use. If you remix, adapt, or build upon the material, you must license the modified material under identical terms.

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a>

