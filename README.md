This script is intended for community edition overleaf servers.

1) Create a git repository where to backup your overleaf projects. Clone it.
2) Fill config.json with your overleaf domain, auth details, project ids, and the path to the repository created in 1)
3) Run python git_sync.py
4) The repo will be synced with git pull
5) The projects specified in config.json will be downloaded to the repository path.
6) The changes will be commited and pushed to the repository.
7) The script can be further automated by running it in a cron job.
