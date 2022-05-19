# GitLab-to GitHub
A Shell Python sicript for transferring repositories from GitLab to GitHub using APIs

## How It Works
1. Create empty private repository on GitHub
2. Clone desired GitLab repository to local temp folder
3. Update remote repo url in the .git/config file of the GitLab repo clone
4. `git push --all` in the GitLab repo clone to push to GitHub repo created in **Step 1**
5. Delete temp folder on local machine

## Usage

### Setup
1. git clone this repo
2. cd into the repo clone
3. create and activate virtual environment
4. `pip install -r requirements.txt` to install dependencies

### Running the Script
`shellpy transferRepos.spy <GITLAB_TOKEN_FILE> <GITHUB_TOKEN_FILE>`

