# Quera Upload Sweetener v1.3

Automate the process of zipping your project, uploading it to Quera, and monitoring the judge results, all from the command line.

## Overview

Quera Upload Sweetener is a Python script designed to streamline the process of submitting projects to Quera, an online coding platform. It zips your project, logs in to Quera, submits the zipped file to a specified problem, and monitors the judging process, providing detailed results once available.

### Features

- **Automated Workflow**: Simply run the script with the necessary arguments, and it handles the rest.
- **Session Management**: Supports session-based login or generates a new session ID if required.
- **Run Sample Test Mode**: Optionally run the submission in Sample Test Mode, allowing you to test your code against sample inputs.
- **Detailed Results**: Provides detailed judging results, including scores and any errors encountered during judging.

## Installation

Ensure you have Python installed on your system. If not, download and install it from [here](https://www.python.org/downloads/).

Install the required dependencies using pip:

```
pip install requests beautifulsoup4
```

Run the script to install `queraups` command for system-wide use:

```
python quera_upload_sweetener.py
```

## Usage

### Command Line Arguments

- `--sessionid` (`-s`): Session ID for Quera login (optional).
- `-gen`: Generate a new session ID by providing a username and password.
- `-kill`: Kill a specified session ID (logout).
- `--url` (`-u`): URL link to the Quera exercise.
- `--prjpath` (`-p`): Project path in your storage (parent of the 'src' folder).
- `--prefix` (`-z`): Prefix for the zip file name.
- `-sts`: Upload in Run Sample Test Mode.
- `--timeout` (`-t`): Timeout for waiting for judging (in seconds).

### JSON Configuration File
The script expects a JSON configuration file named `qconfig.json` in the directory where `queraups` is run. The structure of the JSON file should be as follows:
```json
{
"username": "your_username",
"password": "your_password",
"url": "quera_exercise_url",
"prjpath": "project_path",
"prefix": "zip_file_prefix",
"timeout": 60,
"sessionid": "your_session_id"
}
```

- `username`: Your Quera username.
- `password`: Your Quera password.
- `url`: URL link to the Quera exercise.
- `prjpath`: Project path in your storage. (Parent of the src folder)
- `prefix`: Prefix for the zip file name. (Optional)
- `timeout`: Timeout for waiting for judging in seconds. (Optional)
- `sessionid`: Session ID of Quera login. 
- **Note that: You must provide either Username/Password or SessionID as creditionals**
- **You can generate sessionIDs by `queraups -gen USERNAME PASSWORD`**

## Running Commands

- In first run, you should put the python file in a good directory and run it by python in terminal. The script self-installs itself as `queraups` command system-wide.

- To generate a new session ID: ```queraups -gen your_username your_password```
- To kill a session: ```queraups -kill session_id```
- **For normal submission (with provided qconfig.json in CWD) just need to run:** ```queraups```


```bash
queraups -s <session_id> -u <quera_url> -p <project_path> -z <zip_file_prefix> -t <timeout_seconds>
```

For Upload in "Run Sample Test Mode"
```bash
queraups -sts
```

Now you can use the `queraups` command everywhere after the first run of `python3 quera_upload_sweetener.py`.

## Installation and Usage Notes

1. **Installation Script**: The script includes an installation script (`check_installation()`) to symlink the main script for system-wide use and create the `queraups` command.
2. **Usage**: Ensure you have a `qconfig.json` file in your project path with the necessary Quera login credentials.

## Author
This script was created by AHMZ on 2,3 Farvardin 1403.