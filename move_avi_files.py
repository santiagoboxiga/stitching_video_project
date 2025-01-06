import os
import shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_camera_folders(root_directory):
    """
    Returns a list of camera folders in the root directory.
    """
    camera_folders = []
    for item in os.listdir(root_directory):
        item_path = os.path.join(root_directory, item)
        if os.path.isdir(item_path) and item.lower().startswith('cam'):
            camera_folders.append(item)
    return camera_folders

def get_date_folders(camera_directory):
    """
    Returns a sorted list of date-named folders in the camera directory.
    Assumes folder names are in 'YYYYMMDD' format.
    """
    folders = []
    for item in os.listdir(camera_directory):
        item_path = os.path.join(camera_directory, item)
        if os.path.isdir(item_path):
            # Check if folder name is a valid date
            try:
                datetime.strptime(item, '%Y%m%d')
                folders.append(item)
            except ValueError:
                continue
    # Sort folders by date
    folders.sort()
    return folders

def move_avi_files_up(directory):
    """
    Moves all .avi files in subdirectories up one level and deletes empty folders.

    Parameters:
    - directory: The root directory to start the search.
    """
    # Walk through the directory tree from bottom to top
    for root, dirs, files in os.walk(directory, topdown=False):
        # Skip the date folder itself
        if root == directory:
            continue

        avi_files = [file for file in files if file.endswith('.avi')]
        if not avi_files:
            continue  # Skip if no .avi files

        for file in avi_files:
            current_file_path = os.path.join(root, file)
            destination_path = os.path.join(directory, file)

            # If the destination file already exists, rename the file
            if os.path.exists(destination_path):
                base_name, extension = os.path.splitext(file)
                new_file_name = f"{base_name}_{os.path.basename(root)}{extension}"
                destination_path = os.path.join(directory, new_file_name)
                # Check again in case the new name also exists
                counter = 1
                while os.path.exists(destination_path):
                    new_file_name = f"{base_name}_{os.path.basename(root)}_{counter}{extension}"
                    destination_path = os.path.join(directory, new_file_name)
                    counter += 1
                print(f'Renaming {file} to {new_file_name} to avoid overwrite.')

            try:
                shutil.move(current_file_path, destination_path)
                # print(f'Moved {current_file_path} to {destination_path}')
            except Exception as e:
                print(f'Error moving {current_file_path}: {e}')

        # Delete the directory if it's empty after moving files
        try:
            os.rmdir(root)
            # print(f'Deleted empty directory: {root}')
        except OSError:
            pass  # Directory not empty, skip deletion

def get_last_avi_file_in_folder(folder_path):
    """
    Returns the path of the last .avi file in the folder, sorted by filename.
    """
    try:
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                 if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.avi')]
    except FileNotFoundError:
        return None

    if not files:
        return None
    # Sort files by filename (assumed to reflect time)
    files.sort()
    return files[-1]  # Return the last file

def copy_last_file_to_folder(source_file, destination_folder):
    """
    Copies the source file into the destination folder.
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    destination_file = os.path.join(destination_folder, os.path.basename(source_file))

    # If the destination file already exists, rename it
    if os.path.exists(destination_file):
        base_name, extension = os.path.splitext(os.path.basename(source_file))
        new_file_name = f"{base_name}_copy{extension}"
        destination_file = os.path.join(destination_folder, new_file_name)
        # Check again in case the new name also exists
        counter = 1
        while os.path.exists(destination_file):
            new_file_name = f"{base_name}_copy_{counter}{extension}"
            destination_file = os.path.join(destination_folder, new_file_name)
            counter += 1
        print(f'Renaming copied file to {new_file_name} to avoid overwrite.')

    try:
        shutil.copy2(source_file, destination_file)
        # print(f"Copied {source_file} to {destination_file}")
    except Exception as e:
        print(f'Error copying {source_file} to {destination_file}: {e}')

def process_camera_folder(camera_folder_path):
    date_folders = get_date_folders(camera_folder_path)
    for i in range(len(date_folders)):
        current_folder_name = date_folders[i]
        current_folder_path = os.path.join(camera_folder_path, current_folder_name)

        # Step 1: Move .avi files up one level within the current date folder
        # print(f"\nProcessing date folder: {current_folder_path}")
        move_avi_files_up(current_folder_path)

        # Step 2: Copy the last .avi file from the previous date folder
        if i > 0:
            previous_folder_name = date_folders[i - 1]
            previous_folder_path = os.path.join(camera_folder_path, previous_folder_name)

            # Get the last .avi file from the previous folder
            last_file = get_last_avi_file_in_folder(previous_folder_path)
            if last_file:
                # Copy the last file into the current folder
                copy_last_file_to_folder(last_file, current_folder_path)
            # else:
                # print(f"No .avi files found in {previous_folder_path}, skipping copy.")
        # else:
            # print(f"No previous date folder for {current_folder_name}, skipping copy.")

def process_camera_folders(root_directory):
    camera_folders = get_camera_folders(root_directory)
    with ThreadPoolExecutor() as executor:
        futures = []
        for camera_folder in camera_folders:
            camera_folder_path = os.path.join(root_directory, camera_folder)
            futures.append(executor.submit(process_camera_folder, camera_folder_path))

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing camera folder: {e}")

if __name__ == '__main__':
    root_directory = os.path.dirname(os.path.abspath(__file__))  # Use the script's directory
    process_camera_folders(root_directory)
