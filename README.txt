## Synopsis
This repository contains Python scripts to automate the management, renaming, and processing of .avi video files. The scripts organize, rename, trim, and stitch video files to streamline workflow and ensure efficient processing of camera data.


## Contents

├── move_avi_files.py - Automates moving `.avi` files to the correct directories.
├── video_stitching.py - Handles trimming and stitching `.avi` files based on user input.
└── rename_files.py - Renames `.avi` files with user-defined formats for better organization.


## Dependencies

- os: For file and directory management.
- shutil: For file operations like moving and copying.
- datetime: For parsing and handling dates.
- re: For pattern matching and validation.
- subprocess: Executes external commands (e.g., ffmpeg) for video processing.
- json: Parses ffprobe output for video duration calculations.

Additionally, the video_stitching.py script depends on:

- ffmpeg: A multimedia framework for handling video trimming and concatenation.
- ffprobe: A tool for retrieving video metadata (e.g., duration).
 
##Version information
11/12/2024: Initial release of video management and processing scripts.
