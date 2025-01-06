import os
import datetime
import re

def get_day_suffix(day):
    """Returns the ordinal suffix for a given day."""
    if 11 <= day <= 13:
        return 'th'
    else:
        last_digit = day % 10
        if last_digit == 1:
            return 'st'
        elif last_digit == 2:
            return 'nd'
        elif last_digit == 3:
            return 'rd'
        else:
            return 'th'

def main():
    base_folder = os.path.dirname(os.path.abspath(__file__))

    # Updated pattern to match filenames like '20241031_CAM 75.avi' or '20241031_CAM75.avi'
    filename_pattern = re.compile(r'^(\d{8})_CAM\s*(\d+)\.avi$', re.IGNORECASE)

    # Collect all matching files in the base directory
    all_files_info = []
    for filename in os.listdir(base_folder):
        match = filename_pattern.match(filename)
        if match:
            file_date_str, camera_number = match.groups()
            file_date = datetime.datetime.strptime(file_date_str, '%Y%m%d')
            all_files_info.append({
                'original_filename': filename,
                'date': file_date,
                'camera_number': camera_number
            })

    if not all_files_info:
        print("No files found matching the pattern 'YYYYMMDD_CAMXX.avi' or 'YYYYMMDD_CAM XX.avi' in the base directory.")
        return

    # Process files until the user decides to quit
    processed_files = set()
    while True:
        # Collect user inputs
        site_number = input("\nEnter the site number (e.g., '01'): ").strip()
        location_name = input("Enter the name of the street, intersection, or roundabout: ").strip()
        survey_start_date_str = input("Enter the survey start date (YYYYMMDD): ").strip()

        # Validate and parse the survey start date
        try:
            survey_start_date = datetime.datetime.strptime(survey_start_date_str, '%Y%m%d')
        except ValueError:
            print("Invalid survey start date format. Please use 'YYYYMMDD'.")
            continue

        # Collect camera numbers that share the same inputs
        camera_numbers_input = input("Enter the camera numbers that share these inputs (separated by commas): ").strip()
        camera_numbers = [num.strip() for num in camera_numbers_input.split(',') if num.strip().isdigit()]
        if not camera_numbers:
            print("No valid camera numbers entered.")
            continue

        # Filter files for the specified camera numbers
        files_to_rename = [file_info for file_info in all_files_info if file_info['camera_number'] in camera_numbers]

        if not files_to_rename:
            print("No matching files found for the specified camera numbers.")
            continue

        # Remove files that have already been processed
        files_to_rename = [file_info for file_info in files_to_rename if file_info['original_filename'] not in processed_files]

        if not files_to_rename:
            print("All files for the specified cameras have already been processed.")
            continue

        # Sort files by date and camera number
        files_to_rename.sort(key=lambda x: (x['camera_number'], x['date']))

        # Initialize counters for each camera
        camera_counters = {}

        # Process each file
        for file_info in files_to_rename:
            camera_number = file_info['camera_number']

            # Initialize the counter for the camera if not already done
            if camera_number not in camera_counters:
                camera_counters[camera_number] = 1

            consecutive_number = camera_counters[camera_number]

            # Get day of the week, day with suffix, month, and year
            date = file_info['date']
            day_of_week = date.strftime('%A').upper()
            day = date.day
            day_suffix = get_day_suffix(day)
            month = date.strftime('%B').upper()
            year = date.year
            day_with_suffix = f"{day}{day_suffix}"

            # Construct the new filename
            new_filename = f"{site_number}.{consecutive_number} {location_name} {day_of_week} {day_with_suffix} {month} {year} [CAM {camera_number}].avi"

            # Rename the file
            original_filepath = os.path.join(base_folder, file_info['original_filename'])
            new_filepath = os.path.join(base_folder, new_filename)
            os.rename(original_filepath, new_filepath)
            processed_files.add(file_info['original_filename'])
            print(f"Renamed '{file_info['original_filename']}' to '{new_filename}'.")

            # Increment the counter for the camera
            camera_counters[camera_number] += 1

        # Ask if the user wants to process more cameras
        more_cameras = input("\nDo you want to enter information for additional cameras? (yes/no): ").strip().lower()
        if more_cameras != 'yes':
            break

    print("\nAll files have been renamed successfully.")

if __name__ == '__main__':
    main()
