import os

def create_file(directory: str, file_name: str) -> str:
    """
    Create a file in the specified directory with the given file name.
    If the directory doesn't exist, it will be created.
    If the file already exists, a new file will not be created.

    Args:
        directory (str): The directory path where the file should be created.
        file_name (str): The name of the file.

    Returns:
        str: The full path of the created file.

    Raises:
        OSError: If there is an error while creating the directory or file.

    """
    file_path = os.path.join(directory, file_name)

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Check if the file already exists
    if not os.path.isfile(file_path):
        # Create an empty file
        with open(file_path, 'w') as file:
            pass
        print(f"File created: {file_path}")
    else:
        print(f"File already exists: {file_path}")

    return file_path
