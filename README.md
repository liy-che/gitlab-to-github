# GitLab-to-GitHub
A Python script for importing GitLab repositories into GitHub through APIs

## How It Works
1. Create empty private repository on GitHub
2. Clone desired GitLab repository to local temp folder using `git clone <gitlab-url> <path>`
3. Update remote repo url in GitLab repo clone using `git remote set-url origin <github-url>`
4. Push GitLab repo clone to GitHub repo created in **Step 1** using `git push --all`
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
python importRepos.py <GITLAB_TOKEN_FILE> <GITHUB_TOKEN_FILE>
```
