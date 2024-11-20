import requests
from pathlib import Path
from bs4 import BeautifulSoup
import zipfile
import io
import json
import subprocess

def run_command(command, cwd=None):
    """Run a shell command and handle errors."""
    try:
        subprocess.run(command, cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def download_overleaf_project(config):
    login_url = f"{config['overleaf_url']}/login"
    project_url = f"{config['overleaf_url']}/project"

    # Create a session to persist cookies
    session = requests.Session()

    # Parse the CSRF token
    login_page = session.get(login_url)
    if login_page.status_code != 200:
        print("Failed to load login page.")
        return
    soup = BeautifulSoup(login_page.text, "html.parser")
    csrf_token = soup.find("input", {"name": "_csrf"}).get("value")
    print(f"CSRF token retrieved: {csrf_token}")

    # Step 1: Log in to Overleaf
    login_payload = {
        "email": config['username'],
        "password": config['password'],
        "_csrf": csrf_token
    }
    headers = {
        "Referer": login_url,
        "User-Agent": "Mozilla/5.0"
    }
    response = session.post(login_url, data=login_payload, headers=headers)

    if response.status_code == 200 and "login" not in response.url:
        print("Login successful.")
    else:
        print("Login failed. Check your credentials.")
        return

    for pname, pid in config['projects'].items():
        project_url = f'{config['overleaf_url']}/project/{pid}/download/zip'
        project_outdir = f'{config['repo_path']}/{pname}'
        response = session.get(project_url)

        if response.status_code == 200:
            # Extract the zip file directly from the response
            print("Downloading and extracting project...")
            Path(project_outdir).mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                zip_file.extractall(project_outdir)
            print(f"Project extracted to: {project_outdir}")
        else:
            print(f"Failed to download project. Status code: {response.status_code}")

if __name__ == "__main__":
    print('Loading config')
    config_file = Path(Path(__file__).parent.resolve(),'myconfig.json')
    with open(config_file, 'r') as f:
        config = json.load(f)
    print('Syncing git')
    run_command(["git", "pull"], cwd=config['repo_path'])
    download_overleaf_project(config)
    run_command(["git", "add", "."], cwd=config['repo_path'])
    run_command(["git", "commit", "-m", "Syncing overleaf projects"], cwd=config['repo_path'])
    run_command(["git", "push"], cwd=config['repo_path'])




