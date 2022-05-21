'''
Usage: python transferRepos.py GITLAB_TOKEN_FILE GITHUB_TOKEN_FILE
'''

import sys
import subprocess
import tempfile
import gitlab
from github import Github


def get_token(file_path):
    '''Read in token from file specified by file_path'''
    try:
        with open(file_path, 'r') as f:
            return f.readline()
    except FileNotFoundError:
        print(f'{file_path} does not exist')
        exit(1)


def auth_user(gl_token, gh_token):
    '''Authenicate on gitlab and github'''
    gl = gitlab.Gitlab(url='https://gitlab.umich.edu', private_token=gl_token)

    gh = Github(gh_token)
    return gl, gh


def get_gl(gl, excluded):
    '''Get gitlab projects (all private projects accessible by user and all user's public projects)'''
    gl_projects = gl.projects.list(all=True, visibility='private');
    gl_projects += gl.projects.list(all=True, visibility='public', owned=True)

    gl_projects = [proj for proj in gl_projects if proj.id not in excluded_ids]

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
    	print(f'Usage: python {filename} GITLAB_TOKEN_FILE GITHUB_TOKEN_FILE')
    	exit(1)

    # read in tokens
    gl_token_path = sys.argv[1]
    gh_token_path = sys.argv[2]

    gl_token = get_token(gl_token_path)
    gh_token = get_token(gh_token_path)
    gl, gh = auth_user(gl_token, gh_token)

    # get gitlab projects for transfer
    excluded_ids = [988, 952]
    gl_projects = get_gl(gl, excluded_ids)

    gl.auth()
    gl_user = gl.user.username
    
    # Create private repos on github
    gh_projects = gh.get_user().get_repos(affiliation='owner');
    gh_projects = [proj.name for proj in gh_projects]

    create = input('Confirm making repos?: ').lower()
    added_repos = []

    if (create == 'y' or create == 'yes'):
        with tempfile.TemporaryDirectory() as dir_path:
            for project in gl_projects[:1]:
                new_repo_name = generate_name(gl_user, project, gh_projects, added_repos)
                if (new_repo_name == ''): continue

                # make private repo on github
                new_repo = gh.get_user().create_repo(name=new_repo_name, private=True)
                new_remote_url = new_repo.clone_url
                added_repos.append(new_repo_name)

                # clone gitlab project onto local computer
                proj_url = project.http_url_to_repo
                clone_path = dir_path + '/' + new_repo_name
                # git clone {proj_url} {clone_path}
                subprocess.run(["git", "clone", proj_url, clone_path], stdout=subprocess.DEVNULL)

                # update remote repo url and push to new github repo
                subprocess.run(["git", "-C", clone_path, "remote", "set-url", "origin", new_remote_url], stdout=subprocess.DEVNULL)
                subprocess.run(["git", "-C", clone_path, "push", "--all"], stdout=subprocess.DEVNULL)
                # with Dir(clone_path):
                    # `git remote set-url origin {new_remote_url}
                    # `git push --all

        print('Repos successfully copied to GitHub:')
        for repo in added_repos:
            print(repo)