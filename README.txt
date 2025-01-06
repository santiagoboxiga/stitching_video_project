## Synopsis
This repository contains Python scripts designed to automate the management and processing of .avi video files. The workflow involves organizing .avi files by moving them to appropriate directories and trimming/stitching them into a final processed output.


## Contents

├── move_avi_files.py - Automates moving `.avi` files to the correct directories.
└── video_stitching.py - Handles trimming and stitching `.avi` files based on user input.


## Dependencies

- os: Provides functions for interacting with the operating system.
- shutil: Facilitates file operations, such as moving and copying.
- datetime: Used for parsing and managing dates and times.
- subprocess: Executes external commands (e.g., ffmpeg) for video processing.
- json: Parses ffprobe output for video duration calculations.

Additionally, the video_stitching.py script depends on:

- ffmpeg: A multimedia framework for handling video trimming and concatenation.
- ffprobe: A tool for retrieving video metadata (e.g., duration).
 
##Version information
06/01/2025: Initial release of video management and processing scripts.
