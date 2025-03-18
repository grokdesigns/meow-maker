import os
import re
import base64
import logging
import subprocess
from github import Github
from github.GithubException import GithubException
from github.InputGitAuthor import InputGitAuthor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Getting inputs from environment variables
token = os.environ['TOKEN']
repository = os.environ['REPOSITORY']
source_folder = os.environ['SOURCE_FOLDER']
branch = os.environ['BRANCH']

COMMITTER_NAME = "github-actions[bot]"
COMMITTER_EMAIL = "github-actions[bot]@users.noreply.github.com"

def decode_content(encoded_content):
    """Decode base64 encoded content from GitHub"""
    decoded_bytes = base64.b64decode(encoded_content)
    return decoded_bytes.decode('utf-8')

def upload_file(repo, file_path, content, message, branch):
    """Upload a file to the repository using the specified branch"""
    committer = InputGitAuthor(COMMITTER_NAME, COMMITTER_EMAIL)
    try:
        repo.create_file(
            path=file_path,
            message=message,
            content=content,
            branch=branch,
            committer=committer
        )
        logger.info(f"File '{file_path}' successfully uploaded to '{branch}' branch.")
    except GithubException as e:
        logger.error(f"Failed to upload file '{file_path}' to '{branch}' branch: {e}")

def main():
    """Execute the Tera Processing Workflow"""
    try:
        # Initialize GitHub client and repository
        github_client = Github(token)
        repo = github_client.get_user().get_repo(repository)

        # Create a working directory
        os.makedirs('working', exist_ok=True)

        # Find all .tera files in the source folder
        tera_files = [f for f in os.listdir(source_folder) if f.endswith('.tera')]
        
        for tera_file in tera_files:
            tera_file_path = os.path.join(source_folder, tera_file)
            output_filename = f"generated-themes/{tera_file.replace('.tera', '.md')}"  # Set output file name
            output_path = os.path.join('working', tera_file)  # Path for the working directory

            # Copy the .tera file to the working directory
            with open(tera_file_path, 'r') as fsrc, open(output_path, 'w') as fdst:
                fdst.write(fsrc.read())
                
            # Execute "whiskers" on the copied .tera file
            result = subprocess.run(["whiskers", output_path], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Whiskers execution failed for {output_path}: {result.stderr}")
                continue
            
            logger.info(f"Whiskers executed successfully for {output_path}")
            
            # Read the generated output
            with open(output_path, 'r') as f:
                output_content = f.read()
                
            # Upload the output file back to the GitHub repo
            message = f"🐱 - Generated from {tera_file} via Meow Maker."
            upload_file(repo, output_filename, output_content, message, branch)

    except KeyError as e:
        logger.error(f"Missing required environment variable: {e}.")
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()