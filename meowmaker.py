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
token = os.environ['INPUT_TOKEN']                  # Use INPUT_ prefix
repository = os.environ['INPUT_REPOSITORY']        # Use INPUT_ prefix
source_folder = os.environ['INPUT_SOURCE_FOLDER']                          # Fixed path for GitHub repo templates folder
branch = os.environ['INPUT_BRANCH']                 # Use INPUT_ prefix

COMMITTER_NAME = "github-actions[bot]"
COMMITTER_EMAIL = "github-actions[bot]@users.noreply.github.com"

def decode_content(encoded_content):
    """Decode base64 encoded content from GitHub"""
    decoded_bytes = base64.b64decode(encoded_content)
    return decoded_bytes.decode('utf-8')

def upload_file(repo, file_path, content, message, branch):
    """Upload a file to the repository using the specified branch."""
    committer = InputGitAuthor(COMMITTER_NAME, COMMITTER_EMAIL)
    try:
        # Check if the file already exists
        try:
            existing_file = repo.get_contents(file_path, ref=branch)
            # Update the file with its SHA
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
            if e.status == 404:  # If file does not exist, create it
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
    """Execute the Tera Processing Workflow"""
    try:
        # Initialize GitHub client and repository
        github_client = Github(token)
        repo = github_client.get_user().get_repo(repository)

        # Define the committer once at the start
        committer = InputGitAuthor(COMMITTER_NAME, COMMITTER_EMAIL)

        # Create the working and outputs directory
        os.makedirs('working', exist_ok=True)
        os.makedirs('outputs', exist_ok=True)  # Create the outputs directory

        # Get all .tera files from the repository's templates folder
        contents = repo.get_contents(source_folder, ref=branch)
        tera_files = [file for file in contents if file.path.endswith('.tera')]
        
        changes = []  # Prepare for bulk changes later

        for tera_file in tera_files:
            logger.info(f"Downloading {tera_file.path} from repository.")
            file_content = decode_content(tera_file.content)

            # Save the .tera file to the working directory
            working_file_path = os.path.join('working', tera_file.name)
            with open(working_file_path, 'w') as f:
                f.write(file_content)

            # Change working directory to outputs
            os.chdir('outputs')

            # Execute "whiskers" on the downloaded .tera file
            logger.info(f"Running whiskers on {working_file_path}")
            result = subprocess.run(["/app/whiskers", f"../{working_file_path}"], capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"Whiskers execution failed for {working_file_path}: {result.stderr}")
                continue
            
            logger.info(f"Whiskers executed successfully for {working_file_path}")

            # Prepare for committing changes
            for root, dirs, files in os.walk('.'):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(file_path, start='.')

                    # Construct the message for the commit
                    message = f"🐱 - Generated from {os.path.basename(tera_file.name)} template via Meow Maker"

                    # Read the generated file content
                    with open(file_path, 'r') as f:
                        output_content = f.read()

                    # Store the changes in a tuple (relative_path, output_content, message)
                    changes.append((relative_path, output_content, message))

            os.chdir('..')  # Change back to original working directory after processing

        # After processing all files, make a single commit for all changes
        for relative_path, output_content, message in changes:
            attempts = 3  # Number of retry attempts for conflicts
            for attempt in range(attempts):
                try:
                    existing_file = repo.get_contents(relative_path, ref=branch)  # Get current remote SHA
                    repo.update_file(
                        path=relative_path,
                        message=message,
                        content=output_content,
                        sha=existing_file.sha,
                        branch=branch,
                        committer=committer
                    )
                    logger.info(f"Updated file '{relative_path}' in '{branch}' branch.")
                    break  # Successfully updated, break out of the retry loop
                except GithubException as e:
                    if e.status == 409:  # Handle the SHA conflict
                        logger.warning(f"Conflict updating '{relative_path}', attempt {attempt + 1} of {attempts}. Fetching latest.")
                        # Fetch latest file content to get the new SHA
                        existing_file = repo.get_contents(relative_path, ref=branch)
                        if attempt == attempts - 1:  # Last attempt
                            logger.error(f"Failed to update '{relative_path}' after {attempts} attempts.")
                            raise
                        continue  # Retry with updated SHA
                    elif e.status == 404:  # If file doesn't exist, create a new one
                        repo.create_file(
                            path=relative_path,
                            message=message,
                            content=output_content,
                            branch=branch,
                            committer=committer
                        )
                        logger.info(f"Created file '{relative_path}' in '{branch}' branch.")
                        break  # Created successfully, break out of the loop
                    else:
                        logger.error(f"Failed to upload file '{relative_path}' to '{branch}' branch: {e}")
                        break  # Handle other errors and break

    except KeyError as e:
        logger.error(f"Missing required environment variable: {e}.")
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()