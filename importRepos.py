'''
importRepos.py
Import repositories from source to destination. GitLab is the only supported source at the moment. Destination can be GitLab or GitHub.

Usage: see help menu with 'python importRepos.py -h'
'''

import argparse
import subprocess
import tempfile
from gitlab import Gitlab
from gitlab.exceptions import GitlabAuthenticationError, GitlabListError, GitlabGetError
from github import Github
from github.GithubException import BadCredentialsException
from requests.exceptions import ConnectionError


# TODO
SRC_URL = '' # example: 'https://gitlab.example.com'
DEST_URL = '' # example: 'https://gitlab.example.com'
EXCLUDED_IDS = [] # excluded source project ids for import, example: [123, 345]


def show_error(msg):
    '''Show error message and exit program'''
    print(f'Error: {msg}')
    exit(1)


def get_token(file_path):
    '''Read in token from file specified by file_path'''
    try:
        with open(file_path, 'r') as f:
            return f.readline()
    except FileNotFoundError:
        show_error(f'{file_path} does not exist')


def auth_user(is_dest_gitlab, src_token, dest_token):
    '''Authenicate on source and destination'''
    src = Gitlab(url=SRC_URL, private_token=src_token)
    if is_dest_gitlab:
        dest = Gitlab(url=DEST_URL, private_token=dest_token)
    else: dest = Github(dest_token)
    return src, dest


def get_gitlab_projects(src):
    '''Get projects (for gitlab: all private projects accessible by user and all user's public projects)'''
    projects = src.projects.list(all=True, visibility='private');
    projects += src.projects.list(all=True, visibility='public', min_access_level=30)

    projects = [proj for proj in projects if proj.id not in EXCLUDED_IDS]

    return projects


def generate_name(src_user, project, dest_projects, added_repos):
    '''Generate new name for destination repo'''
    new_name = '-'.join(project.name.split())
    proj_user = project.owner['username']
    if (proj_user != src_user):
        new_name = proj_user + '-' + new_name

    while ((new_name.lower() in dest_projects) or (new_name.lower() in added_repos)):
        new_name = input(f'{new_name} already exists, input a new name or enter to skip: ')

    return new_name


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                prog='importRepos.py',
                description='Import repositories from source to destination. Gitlab is the only supported source at the moment. Destination can be Gitlab or GitHub.')
    parser.add_argument('-l', '--gitlab', action='store_true', help='specifies that the destination is gitlab')
    parser.add_argument('srcSecret', metavar='srcSecret.txt', help='File that contains only the secret key for the source API')
    parser.add_argument('destSecret', metavar='destSecret.txt', help='File that contains only the secret key for the destination API')
    args = parser.parse_args()

    src, dest = auth_user(args.gitlab, get_token(args.srcSecret), get_token(args.destSecret))

    # SOURCE
    try:
        src.auth()
    except (ConnectionError, GitlabGetError) as _:
        show_error('Connection failed. Check source url (must be Gitlab).')
    except GitlabAuthenticationError:
        show_error('Authentication failed. Check source/Gitlab token and URLs.')
    src_user = src.user.username

    # get source projects for import
    src_projects = get_gitlab_projects(src)

    # DESTINATION
    # get existing projects at destination
    try:
        if args.gitlab:
            dest_projects = get_gitlab_projects(dest)
        else: dest_projects = dest.get_user().get_repos(affiliation='owner')
    except GitlabListError:
        show_error('Check Gitlab destination URL.')

    try:
        dest_projects = [proj.name.lower() for proj in dest_projects]
    except BadCredentialsException:
        show_error('Authentication failed. Check GitHub destination token. Or, if the destination is Gitlab, add -l flag.')

    create = input('Confirm making repos?: ').lower()
    added_repos = []

    if (create == 'y' or create == 'yes'):
        with tempfile.TemporaryDirectory() as dir_path:
            for project in src_projects:
                print('Importing (' + project.name + ')')
                new_repo_name = generate_name(src_user, project, dest_projects, added_repos)
                if (new_repo_name == ''): continue

                # make private repo in destination
                if args.gitlab:
                    new_repo = dest.projects.create({'name': new_repo_name, 'visibility': 'private'})
                else: new_repo = dest.get_user().create_repo(name=new_repo_name, private=True)
                
                new_remote_url = new_repo.ssh_url_to_repo
                added_repos.append(new_repo_name)

                # clone source project onto local computer
                proj_url = project.http_url_to_repo
                clone_path = dir_path + '/' + new_repo_name
                subprocess.run(["git", "clone", proj_url, clone_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                # update remote repo url and push to new destination repo
                subprocess.run(["git", "-C", clone_path, "remote", "set-url", "origin", new_remote_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(["git", "-C", clone_path, "push", "--all"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                print('--------------------------------------------------------')

        print('Repos successfully copied to destination:')
        for repo in added_repos:
            print(repo)