# GitLab-to-GitHub
A Python script for importing GitLab repositories into GitHub and GitLab through APIs

## How It Works
1. Create empty private repository on GitHub / GitLab
2. Clone desired GitLab repository to local temp folder using `git clone <gitlab-url> <path>`
3. Update remote repo url in GitLab repo clone using `git remote set-url origin <new-repo-url>`
4. Push GitLab repo clone to repo created in **Step 1** using `git push --all`
5. Delete temp folder on local machine

## Usage

### Setup
1. Generate access tokens and put each in a separate text file
2. Git clone this repo
3. Cd into the repo clone
4. Create and activate virtual environment ([tutorial](https://python.land/virtual-environments/virtualenv))
5. Install dependencies
6. Complete TODO at the top of importRepos.py
```
git clone https://github.com/liy-che/gitlab-to-github.git
cd gitlab-to-github
python -m venv venv
pip install -r requirements.txt
# open and complete importRepos.py TODO
```

### Running the Script
```
python importRepos.py [-h] [-l] srcSecret.txt destSecret.txt

positional arguments:
  srcSecret.txt   File that contains only the secret key for the source API
  destSecret.txt  File that contains only the secret key for the destination API

optional arguments:
  -h, --help      show this help message and exit
  -l, --gitlab    specifies that the destination is gitlab
```
