'''
Usage: python importRepos.py GITLAB_TOKEN_FILE GITHUB_TOKEN_FILE
'''

import os
import sys
import subprocess
import tempfile
from gitlab import Gitlab
from gitlab.exceptions import GitlabAuthenticationError
from github import Github
from github.GithubException import BadCredentialsException
from requests.exceptions import ConnectionError


# TODO
GITLAB_URL = 'https://gitlab.eecs.umich.edu' # example: 'https://gitlab.example.com'
EXCLUDED_IDS = [988, 952] # excluded gitlab project ids for import, example: [123, 345]


def show_error(msg):
    '''Show error message and exit program'''
    print(msg)
    exit(1)


def get_token(file_path):
    '''Read in token from file specified by file_path'''
    try:
        with open(file_path, 'r') as f:
            return f.readline()
    except FileNotFoundError:
        show_error(f'{file_path} does not exist')


def auth_user(gl_token, gh_token):
    '''Authenicate on gitlab and github'''
    gl = Gitlab(url=GITLAB_URL, private_token=gl_token)
    gh = Github(gh_token)
    return gl, gh


def get_gl_projects(gl):
    '''Get gitlab projects (all private projects accessible by user and all user's public projects)'''
    gl_projects = gl.projects.list(all=True, visibility='private');
    gl_projects += gl.projects.list(all=True, visibility='public', owned=True)

    gl_projects = [proj for proj in gl_projects if proj.id not in EXCLUDED_IDS]

    return gl_projects


def generate_name(gl_user, project, gh_projects, added_repos):
    '''Generate new name for github repo'''
    new_name = project.name
    proj_user = project.owner['username']
    if (proj_user != gl_user):
        new_name = proj_user + '-' + new_name

    while (new_name in gh_projects or new_name in added_repos):
        new_name = input(f'{new_name} already exists, input a new name or enter to skip: ')

    return new_name


if __name__ == '__main__':
    if (len(sys.argv) != 3):
        filename = os.path.basename(__file__)
        show_error(f'Usage: python {filename} GITLAB_TOKEN_FILE GITHUB_TOKEN_FILE')

    # read in tokens
    gl_token_path = sys.argv[1]
    gh_token_path = sys.argv[2]

    gl_token = get_token(gl_token_path)
    gh_token = get_token(gh_token_path)
    gl, gh = auth_user(gl_token, gh_token)

    try:
        gl.auth()
    except ConnectionError:
        show_error('Connection failed. Check GitLab url')
    except GitlabAuthenticationError:
        show_error('Authentication failed. Check GitLab token')
    gl_user = gl.user.username

    # get gitlab projects for import
    gl_projects = get_gl_projects(gl)

    # Create private repos on github
    gh_projects = gh.get_user().get_repos(affiliation='owner');

    try:
        gh_projects = [proj.name for proj in gh_projects]
    except BadCredentialsException:
        show_error('Authentication failed. Check GitHub token')

    create = input('Confirm making repos?: ').lower()
    added_repos = []

    if (create == 'y' or create == 'yes'):
        with tempfile.TemporaryDirectory() as dir_path:
            for project in gl_projects:
                new_repo_name = generate_name(gl_user, project, gh_projects, added_repos)
                if (new_repo_name == ''): continue

                # make private repo on github
                new_repo = gh.get_user().create_repo(name=new_repo_name, private=True)
                new_remote_url = new_repo.clone_url
                added_repos.append(new_repo_name)

                # clone gitlab project onto local computer
                proj_url = project.http_url_to_repo
                clone_path = dir_path + '/' + new_repo_name
                subprocess.run(["git", "clone", proj_url, clone_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                # update remote repo url and push to new github repo
                subprocess.run(["git", "-C", clone_path, "remote", "set-url", "origin", new_remote_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(["git", "-C", clone_path, "push", "--all"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print('Repos successfully copied to GitHub:')
        for repo in added_repos:
            print(repo)