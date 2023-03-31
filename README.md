This repository includes some Python scripts to help you with the Vocareum platform via its REST API.

# Creating the access token

As the Vocareum REST API uses a token-based authentication, you need to create a token in your Vocareum account. You can create a token by going to your profile page, "Settings" option and "Personal Access Tokens" tab. 

Once you have created the token, you need to create a file called `TOKEN` in the root folder and paste the token in its first line.

# `vc_helper.py`

This is the main script. The script currently has two working modes. The first one is to list the available courses and the second one is to extract the files from a given course into a given directory.

## Listing the available courses

This option lists the available courses visible to the user. The output follows the pattern:

```
COURSE_ID: COURSE_NAME
```

## Extracting the files into a directory

This option accesses to a given course and extracts the files into a given directory. 

The options to given in the command line are:
* `-e`: the course ID to extract (see `-l` option to know the available course ids)
* `-t`: the target directory to extract the files

The format will be:

```bash
python vc_helper -e <course_id> -t <target_path>"
```

The set of files that are extracted are indicated in the `FILES` variable in the script, which currently cover the most important files (and others required in our courses) are:

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

# Contributing

This project was just a quick side project to help me to deal with Vocareum interface, but if you want to contribute, any comment is welcome! If you are interested in contributing to this project, please read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

Just remember that:

1. Anyone participating will be subject to and agrees to sign on to the [Code of Conduct](CODE_OF_CONDUCT.md).

2. The development and community management of this project follows the governance rules described in the [GOVERNANCE.md](GOVERNANCE.md) document.

# License

This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>

The [CC BY-SA](https://creativecommons.org/licenses/by-sa/4.0/) license allows reusers to distribute, remix, adapt, and build upon the material in any medium or format, so long as attribution is given to the creator. The license allows for commercial use. If you remix, adapt, or build upon the material, you must license the modified material under identical terms.

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a>

