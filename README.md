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

### Example Usage

```bash
queraups -s <session_id> -u <quera_url> -p <project_path> -z <zip_file_prefix> -t <timeout_seconds>
```

Now you can use the `queraups` command everywhere instead of `python3 quera_upload_sweetener.py`.

## Installation and Usage Notes

1. **Installation Script**: The script includes an installation script (`check_installation()`) to symlink the main script for system-wide use and create the `queraups` command.
2. **Usage**: Ensure you have a `qconfig.json` file in your project path with the necessary Quera login credentials.
