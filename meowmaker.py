import os
import base64
import logging
import subprocess
import hashlib
import json
from github import Github, GithubException, InputGitAuthor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Getting inputs from environment variables
token = os.environ['INPUT_TOKEN']                  
repository = os.environ['INPUT_REPOSITORY']        
source_folder = os.environ['INPUT_SOURCE_FOLDER']   
branch = os.environ['INPUT_BRANCH']                 

COMMITTER_NAME = "github-actions[bot]"
COMMITTER_EMAIL = "github-actions[bot]@users.noreply.github.com"
TRACKING_FILE = 'tera_sha_tracking.json'           

def decode_content(encoded_content):
    """Decode base64 encoded content from GitHub."""
    decoded_bytes = base64.b64decode(encoded_content)
    return decoded_bytes.decode('utf-8')

def load_sha_tracking():
    """Load SHA tracking from the JSON file. If it does not exist, return an empty dictionary."""
    if not os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'w') as f:
            json.dump({}, f)
        return {}
    with open(TRACKING_FILE, 'r') as f:
        return json.load(f)

def save_sha_tracking(tracking_data):
    """Save the SHA tracking to the JSON file."""
    with open(TRACKING_FILE, 'w') as f:
        json.dump(tracking_data, f, indent=4)

def compute_sha256(file_path):
    """Compute the SHA-256 hash of the specified file."""
    with open(file_path, 'rb') as f:
        content = f.read()
    return hashlib.sha256(content).hexdigest()

def upload_file(repo, file_path, content, message):
    """Upload a file to the repository using the specified branch."""
    committer = InputGitAuthor(COMMITTER_NAME, COMMITTER_EMAIL)
    try:
        try:
            existing_file = repo.get_contents(file_path, ref=branch)
            repo.update_file(
                path=file_path,
                message=message,
                content=content,
                sha=existing_file.sha,
                branch=branch,
                committer=committer
            )
            logger.info(f"File '{file_path}' successfully updated in '{branch}' branch.")
        except GithubException as e:
            if e.status == 404:
                repo.create_file(
                    path=file_path,
                    message=message,
                    content=content,
                    branch=branch,
                    committer=committer
                )
                logger.info(f"File '{file_path}' successfully uploaded to '{branch}' branch.")
            else:
                logger.error(f"Failed to upload file '{file_path}' to '{branch}' branch: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while uploading file '{file_path}': {e}")

def main():
    """Execute the Tera Processing Workflow."""
    try:
        github_client = Github(token)
        repo = github_client.get_user().get_repo(repository)

        previous_sha_tracking = load_sha_tracking()

        os.makedirs('working', exist_ok=True)
        os.makedirs('outputs', exist_ok=True)

        contents = repo.get_contents(source_folder, ref=branch)
        tera_files = [file for file in contents if file.path.endswith('.tera')]

        output_files_to_upload = []
        current_sha_tracking = {}

        # Process each Tera file
        for tera_file in tera_files:
            logger.info(f"Downloading {tera_file.path} from repository.")
            file_content = decode_content(tera_file.content)

            working_file_path = os.path.join('working', tera_file.name)
            with open(working_file_path, 'w') as f:
                f.write(file_content)  

            sha256 = compute_sha256(working_file_path)
            current_sha_tracking[tera_file.path] = sha256

            previous_sha = previous_sha_tracking.get(tera_file.path)
            if previous_sha == sha256:
                logger.info(f"SHA256 of '{tera_file.path}' matches previously stored SHA. Skipping Whiskers.")
                continue

            logger.info(f"Running whiskers on '{working_file_path}'.")
            result = subprocess.run(["/app/whiskers", working_file_path], capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"Whiskers execution failed for '{working_file_path}': {result.stderr}")
                continue

            logger.info(f"Whiskers executed successfully for '{working_file_path}'")

            # New logging to check outputs directory
            generated_files = []
            for root, _, files in os.walk('outputs'):
                for file_name in files:
                    output_file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(output_file_path, start='outputs')

                    with open(output_file_path, 'r') as f:
                        output_content = f.read()

                    message = f"🐱 - Generated from {os.path.basename(tera_file.name)} template via Meow Maker. [no ci]"
                    output_files_to_upload.append((relative_path, output_content, message))
                    generated_files.append(relative_path)  # Collect generated files for logging

            # Log all generated files
            if generated_files:
                logger.info(f"Generated files: {', '.join(generated_files)}")
            else:
                logger.warning("No files generated by Whiskers.")

        # Final upload logic...
        for file_path, content, message in output_files_to_upload:
            upload_file(repo, file_path, content, message)

    except KeyError as e:
        logger.error(f"Missing required environment variable: {e}.")
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()