#!/usr/bin/env python3
########################################################################
# Quera Upload Sweetener v1.4 (Zip project + Upload to Quera + Show detailed judge result)
# By AHMZ - 2,3 Farvardin 1403
# if you don't have dependencies, run command below:
# pip install requests beautifulsoup4
########################################################################
import os
import sys
import ctypes
from bs4 import BeautifulSoup
import argparse
import datetime
import json
import requests
import time
import zipfile
########################################################################
ansi = {
    'bold': '\033[1m',
    'dim': '\033[2m',
    'green': '\033[32m',
    'lgreen': '\033[92m',
    'red': '\033[31m',
    'lred': '\033[91m',
    'blue': '\033[34m',
    'lblue': '\033[94m',
    'yellow': '\033[33m',
    'lyellow': '\033[93m',
    'cyan': '\033[36m',
    'lcyan': '\033[96m',
    'magenta': '\033[35m',
    'lmagenta': '\033[95m',
    'reset': '\033[0m'
}
########################################################################
def check_installation():
    if sys.platform == 'win32':
        scname = 'queraups.cmd'
        ppath = f'C:\\Windows\\{scname}'
        mabspath = os.path.abspath(sys.argv[0])
        scontent = f'@echo off\npython "{mabspath}" %*'
        sfpath = os.path.join(os.path.split(mabspath)[0], scname)
        linkcmd = f'cmd /c mklink {ppath} "{sfpath}" >nul 2>&1'
        # create the bash/batch file
        if not os.path.isfile(sfpath):
            with open(sfpath, 'w') as f: f.write(scontent)
    else:
        scname = 'queraups'
        ppath = f'/usr/local/bin/{scname}'
        mabspath = os.path.abspath(sys.argv[0])
        linkcmd = f'sudo ln -sT "{mabspath}" {ppath}'

    # create symlink in system path
    if not os.path.islink(ppath):
        if sys.platform == 'win32' and not ctypes.windll.shell32.IsUserAnAdmin():
            print('\nRunning script as administrator for installing in system ...')
            assert (ctypes.windll.shell32.ShellExecuteW(None, 'runas', 'python', f'"{mabspath}"', None, 1) > 32), 'Run as admin failed!'
            print(f'\n{ansi["bold"]}Please check the opened window.{ansi["reset"]}\n')
            exit(0)
        assert os.system(linkcmd) == 0, 'Failed to create link . Run the script as an administrator.'
        print(f'{ansi["lgreen"]}Successfully installed the script on the system.{ansi["reset"]}')
        print(f"You can use command {ansi['bold']}'queraups'{ansi['reset']} from everywhere .")
        print(f"Note: First, create qconfig.json in the directory where 'queraups' will be run.")
        print(f"To uninstall 'queraups' just delete the file {ppath}")
        input('\nPress Enter to exit...')
        exit(0)
########################################################################
def __parse_arguments__(cmd_args):
    """ Validate and parse the arguments from cmd_args and json file qconfig.json in root of project path """
    if cmd_args.gen: # Generate flag provided!
        assert cmd_args.gen[0][0] and cmd_args.gen[0][1] , "Not enough arguments!"
        # Only perform login and generate session_id
        print('Performing Login and generating session_id ....')
        session = login_to_quera(username=cmd_args.gen[0][0], password=cmd_args.gen[0][1])
        print(f"{ansi['lgreen']}Login Successfully. Generated session_id is shown below:{ansi['reset']}\n")
        print(ansi['bold'] + session.cookies['session_id'] + ansi['reset'])
        print(f"\n {ansi['lcyan']}Please keep it somewhere secure.{ansi['reset']}")
        exit(0)
    if cmd_args.kill: # Kill flag provided!
        assert cmd_args.kill[0][0], "Provide a session id!"
        # Only perform logout! (Killing given session_id)
        print('Performing Logout and killing session_id ....')
        session = login_to_quera(sessionid=cmd_args.kill[0][0])
        logout_quera(session)
        print("Session killed.")
        exit(0)
    json_file_path = None
    if cmd_args.prjpath: json_file_path = cmd_args.prjpath + '/qconfig.json'
    if not (json_file_path and os.path.isfile(json_file_path)): json_file_path = 'qconfig.json'
    assert os.path.isfile(json_file_path), 'No JSON config file provided! Please put a valid JSON config file in your project path (or CWD)'
    with open(json_file_path, 'r') as json_file:
        args_json = json.load(json_file)
        # If no session-id provided, assert username and password
        if not args_json.get('sessionid'):
            assert args_json.get('username'), 'No user specified! You Must specify your userpass in JSON config file.'
            assert args_json.get('password'), 'No password specified! You Must specify your userpass in JSON config file.'
        for key, value in args_json.items():
            if not getattr(cmd_args, key, None): setattr(cmd_args, key, value)
        assert cmd_args.url, 'Please provide a url for Quera Exercise Problem! (with -u or in JSON file)'
        assert cmd_args.prjpath and os.path.isdir(cmd_args.prjpath+'/src'), "Please provide a project path in your storage (The parent of 'src' dir)"
        # If name_prefix is not provided, set it to empty
        if not getattr(cmd_args, 'prefix', None): setattr(cmd_args, 'prefix', '')
        # If timeout is not provided, set it to 60 seconds
        if not getattr(cmd_args, 'timeout', None): setattr(cmd_args, 'timeout', 60)
        # If sessionid is not provided, set it to None
        if not getattr(cmd_args, 'sessionid', None): setattr(cmd_args, 'sessionid', None)
    return cmd_args
########################################################################
def __zip_project__(folder_path, zip_path):
    """ Private function to zip a folder content into a .zip file """
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))
########################################################################
def __get_headers__(session):
    session_id = session.cookies.get('session_id', domain='quera.org')
    if not session_id: session_id = session.cookies.get('session_id', domain='.quera.org')
    if not session_id: session_id = session.cookies.get('session_id')
    csrf_token = session.cookies.get('csrf_token', domain='quera.org')
    if not session_id: csrf_token = session.cookies.get('csrf_token', domain='.quera.org')
    if not session_id: csrf_token = session.cookies.get('csrf_token')
    return {
        'cookie': f"csrf_token={csrf_token}; session_id={session_id};",
        'origin': 'https://quera.org',
        'x-csrftoken': csrf_token,
    }
########################################################################
def __send_request_with_csrf__(session, url, data={}, files=None):
    """ Send HTTP post request with CSRF token (fetched by get request) """
    csrf_token_input = BeautifulSoup(session.get(url).text, 'html.parser').find('input', {'name': 'csrfmiddlewaretoken'})
    assert csrf_token_input, "Cannot find the csrfmiddlewaretoken!" 
    data['csrfmiddlewaretoken'] = csrf_token_input.get('value')
    response = session.post(url, headers={'origin': 'https://quera.org'}, data=data, files=files)
    if response.status_code != 200:
        return False, response
    return True, response
########################################################################
########################################################################
########################################################################
def make_zip(proj_path, zip_name):
    """ Create the submission zip file from project path and save it on <PRJPATH>/zip/* with datetime """
    # Define initial zip location
    os.makedirs(f'{proj_path}/zip/', exist_ok=True)
    zip_location = f'{proj_path}/zip/{zip_name}.zip'
    # Check if the zip location already exists
    i = 1
    while os.path.exists(zip_location):
        # If it exists, add a numerical suffix to the zip name and check again
        zip_location = f'{proj_path}/zip/{zip_name}_{i}.zip'
        i += 1
    # Create the zip file
    __zip_project__(proj_path+'/src/', zip_location)
    return zip_location
########################################################################
def login_to_quera(sessionid=None, username=None, password=None):
    """ Login to Quera platform using provided credentials and returns logined session """
    session = requests.Session()
    if sessionid:
        session.cookies.set('session_id', sessionid)
        success = session.get('https://quera.org/profile/').url == 'https://quera.org/profile/'
        assert success, 'Session id has been expired or invalid!!'
    else:
        success, response = __send_request_with_csrf__(session, 'https://quera.org/accounts/login',
                                                       {'login': username, 'password': password})
        assert success, f'Response Code is not OK. (Code = {response.status_code})'
        assert session.cookies.get('session_id'), 'Login Failed! Please check your username and password!'
    return session
########################################################################
def logout_quera(session):
    """ Log out of Quera platform using current logged in session """
    success, response = __send_request_with_csrf__(session, 'https://quera.org/accounts/logout')
    assert success, "Logging Out Failed!"
    return
########################################################################
def submit_file_for_problem(session, problem_url, file_path, sts):
    """ Submit a file to specified problem URL in Quera """
    assert os.path.isfile(file_path), 'The provided file does not exist.'
    submission_id = None
    trys = 3
    while not submission_id:
        success, response = __send_request_with_csrf__(session,
                                                       problem_url, 
                                                       {'file_type': '34', 'type': 'STS' if sts else 'JS'},
                                                       files={'file': open(file_path, 'rb')})
        assert success, f'Response Code is not OK. (Code = {response.status_code})'
        # Get submission id from response
        all_rows = BeautifulSoup(response.text, 'html.parser').find_all('tr')
        for row in all_rows:
            if 'data-submission_id' in row.attrs:
                submission_id = int(row['data-submission_id'])
                break
        if trys <= 1:
            assert submission_id, "Can't find the submission id."
        elif not submission_id:
            response = session.get(response.url)
            trys -= 1
    # Returns submission ID and Results page URL
    return submission_id, response.url
########################################################################
def wait_for_judge(session, submissions_page_url, submission_id, timeout):
    """ Wait until quera finishes judging the submission with given id (then returns parsed table row and judging time) """
    start_time = time.time() # Define start time
    while True: # Wait for judge
        assert time.time() - start_time < timeout, f'Timeout reached ({timeout} seconds).' # Check if timeout reached
        response = session.get(submissions_page_url)
        assert response.status_code == 200, f'Response Code is not OK. (Code = {response.status_code})'
        # Find related table row
        submission_soup = BeautifulSoup(response.text, 'html.parser').find('tr', {'data-submission_id': f'{submission_id}'})
        # If there is not a yellow label (Waiting for judge...)  then it has been judged
        if len(submission_soup.findAll(class_='ui yellow label')) == 0 :
            # Returns submission_soup, and judging time
            return submission_soup, time.time() - start_time
        time.sleep(1) # Wait for 1 second before next check
########################################################################
def get_detailed_result(session, submission_id, sts):
    """ Obtain the detailed result (passed testcases, etc ...) of given submission id , and Get log if STS mode """
    trys = 3
    while True:
        response = session.post('https://quera.org/assignment/submission_action',
                                headers=__get_headers__(session),
                                data={'action': 'get_judge_log' if sts else 'get_result',
                                    'submission_id': f'{submission_id}'})
        if response.status_code == 200: break
        elif trys <= 1: raise AssertionError(f'Response Code is not OK. (Code = {response.status_code})')
        else: trys -= 1
    assert response.json()['success'] is True, 'Not successful ...'
    return response.json()
########################################################################
def convert_html_to_ansi(html):
    """ Converts HTML to ANSI printable text in terminal (with colors) """
    # Parse HTML text
    soup = BeautifulSoup(html, 'html.parser')
    # Find all elements with inline style and replace them with ANSI escape codes
    for tag in soup.find_all():
        _style = tag.get('style')
        _class = tag.get("class")
        if (_style and ('color:green' in _style)) or (_class and ('shj_g' in _class)):
            tag.string = f"{ansi['lgreen']}{tag.string}{ansi['reset']}"
        elif (_style and ('color:red' in _style)) or (_class and ('shj_r' in _class)):
            tag.string = f"{ansi['lred']}{tag.string}{ansi['reset']}"
        elif (_style and ('color:blue' in _style)) or (_class and ('shj_b' in _class)):
            tag.string = f"{ansi['lblue']}{tag.string}{ansi['reset']}"
        elif (_style and ('color:orange' in _style)) or (_class and ('shj_o' in _class)):
            tag.string = f"{ansi['yellow']}{tag.string}{ansi['reset']}"
    # Get the modified text
    return soup.get_text()
########################################################################
########################################################################
########################################################################
def main(args):
    error = 0
    try:
        # Zip project files
        print('Zipping stage:', end=' ', flush=True)
        zip_location = make_zip(args.prjpath, args.prefix + datetime.datetime.now().strftime('%Y%m%d_%H%M'))
        print(f"{ansi['lgreen']}Successful{ansi['reset']}")

        # Login to Quera
        print('Login stage:', end=' ', flush=True)
        if args.sessionid:
            session = login_to_quera(sessionid=args.sessionid)
            print(f"{ansi['lgreen']} Already OK (by session_id){ansi['reset']}")
        else:
            session = login_to_quera(username=args.username, password=args.password)
            print(f"{ansi['lgreen']}Successful{ansi['reset']}")
        
        # Submit file in Quera
        if args.sts: print(ansi['lmagenta'] + 'Run Sample Test Mode' + ansi['reset'])
        print('Submit stage:', end=' ', flush=True)
        submission_id, submissions_url = submit_file_for_problem(session, args.url, zip_location, args.sts)
        print(f"{ansi['lgreen']}Successful with id {ansi['bold']}{submission_id}{ansi['reset']}")

        # Wait for quera judge result
        print(f"\n{ansi['lyellow']}Waiting For Quera Judge ....{ansi['reset']}")
        submission_soup, judge_time = wait_for_judge(session, submissions_url, submission_id, args.timeout)

        # print bare score and judging time
        if not args.sts:
            print(f"\n{ansi['cyan']}You got score {ansi['bold']}{int(submission_soup.find_all('td')[7].get_text(strip=True))}{ansi['reset']}",
                  end=' ', flush=True)
        print(f"(Judged in {ansi['bold']}%d{ansi['reset']} seconds)\n" % judge_time)
        
        # get the detailed result via request
        results_html = get_detailed_result(session, submission_id, False)['result']

        # print the detailed result in color
        print(convert_html_to_ansi(results_html))

        # If in Run Sample Test Mode, print more details and judge log
        if args.sts:
            print(f"\n{ansi['bold']}{ansi['lmagenta']} More Details (Judge Log for Sample Test Run):{ansi['reset']}")
            judge_log = get_detailed_result(session, submission_id, True)['result']
            print(convert_html_to_ansi(judge_log))

    except Exception as e:
        print(f"{ansi['lred']}Failed:\n{repr(e)}{ansi['reset']}")
        error = 1
    finally:
        if not args.sessionid:
            logout_quera(session)
            print("Successfully logged out.")
        exit(error)
########################################################################
########################################################################
if __name__ == "__main__":
    try:
        check_installation()
    except Exception as e:
        print(f"{ansi['lred']}Error in installing queraups:\n{repr(e)}{ansi['reset']}")
        exit(127)
    parser = argparse.ArgumentParser(description='Quera Judge Python code (Zip project + Upload to Quera + Wait for result) By AHMZ')
    parser.add_argument('--sessionid', '-s', type=str, help='Session ID of quera login! ( for not to use userpass :) )')
    parser.add_argument('-gen', action='append', nargs=2, metavar=('username','password'), help='Generate a new session ID')
    parser.add_argument('-kill', action='append', nargs=1, metavar=('sessionid'), help='Kill given session ID (logout)')
    parser.add_argument('--url', '-u', type=str, help='URL Link to Quera Exercise')
    parser.add_argument('--prjpath', '-p', type=str, help='Project path in your storage (Attention: The parent of src folder!!)')
    parser.add_argument('--prefix', '-z', type=str, help='Zip file name prefix')
    parser.add_argument('-sts', dest='sts', action='store_true', help='Upload in Run Sample Test Mode')
    parser.add_argument('--timeout', '-t', type=int, help='Time out for wait for judging in seconds')
    try:
        parsed_args = __parse_arguments__(parser.parse_args())
    except Exception as e:
        print(f"{ansi['lred']}Argument parsing failed:\n{repr(e)}{ansi['reset']}")
        exit(1)
    main(parsed_args)