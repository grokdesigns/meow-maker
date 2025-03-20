import os
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_directory_structure(start_path, level=0, max_depth=1):
    """Recursively prints the directory structure, limited to max_depth."""
    if level > max_depth:  # Stop recursion if max depth is exceeded
        return
    with os.scandir(start_path) as entries:
        for entry in entries:
            print('    ' * level + '|-- ' + entry.name)
            if entry.is_dir():
                print_directory_structure(entry.path, level + 1, max_depth)

def log_files_in_directory(directory):
    # List all items in the given directory
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        
        # Check if the item is a directory
        if os.path.isdir(item_path):
            # If the item is a directory, call the function recursively
            log_files_in_directory(item_path)
        else:
            # Otherwise, log the file
            logger.info(f"  - {item}, Size: {os.path.getsize(item_path)} bytes")

def main():
    """Execute the Tera Processing Workflow."""
    try:
        # Change the working directory to the output folder
        os.chdir("/workspace")

        # Get the root directory to reference the folder locations correctly
        root_dir = os.getcwd()  # This should be '/workspace' inside the container

        # Set the input and output folders; ensure they have sensible defaults
        input_folder = os.path.join(root_dir, os.environ.get('SRCFOLDER', 'templates'))
        output_folder = os.path.join(root_dir, os.environ.get('DSTFOLDER', 'output'))

        # Log the resolved paths for verification
        logger.info(f"SRCFOLDER (Input): {input_folder}")
        logger.info(f"DSTFOLDER (Output): {output_folder}")

        # Check if the input_folder exists
        if not os.path.exists(input_folder):
            raise FileNotFoundError(f"Error: Input directory '{input_folder}' does not exist.")

        # Log the contents of the input folder
        logger.info("Logging contents of the input folder:")
        for filename in os.listdir(input_folder):
            logger.info(f"  - {filename}")

        # Get the list of Tera files in the input folder
        tera_files = [f for f in os.listdir(input_folder) if f.endswith('.tera')]

        # Change the working directory to the output folder
        os.chdir(output_folder)

        # Process each Tera file
        for tera_file in tera_files:
            working_file_path = os.path.join(input_folder, tera_file)  # Full path to the Tera file

            # Run whiskers with the full path to the Tera file
            result = subprocess.run(["/app/whiskers", working_file_path],
                                    capture_output=True,
                                    text=True)

            # Log stdout and stderr for debugging
            logger.info(f"Processing '{working_file_path}': {result.stdout}")
            if result.returncode != 0:
                logger.error(f"Whiskers execution failed for '{working_file_path}': {result.stderr}")
                continue

            logger.info(f"Whiskers executed successfully for '{working_file_path}'")
            # Add this right after processing files in your meowmaker.py

        logger.info("Generated files in outputs directory:")
        log_files_in_directory(output_folder)
                
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")

if __name__ == "__main__":
    main()