import os
import datetime
import subprocess

def parse_filename(filename):
    """
    Parses the filename to extract the start time.

    Expected filename format: '1_YYYYMMDD-HHMMSS_XXXXh'

    Returns:
        datetime.datetime object representing the start time, or None if parsing fails.
    """
    basename = os.path.basename(filename)
    name, _ = os.path.splitext(basename)
    parts = name.split('_')
    if len(parts) < 2:
        return None
    datetime_str = parts[1]
    try:
        start_time = datetime.datetime.strptime(datetime_str, '%Y%m%d-%H%M%S')
        return start_time
    except ValueError:
        return None

def get_video_duration(filename):
    """
    Gets the duration of the video in seconds using ffprobe.

    Returns:
        Duration in seconds, or None if it fails.
    """
    import json
    cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=duration',
        '-of', 'json',
        filename
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        return None
    try:
        output = json.loads(result.stdout)
        duration = float(output['streams'][0]['duration'])
        return duration
    except (KeyError, IndexError, ValueError, json.JSONDecodeError):
        return None

def main():
    start_time_str = input('Enter desired start time (YYYY-MM-DD HH:MM:SS): ')
    end_time_str = input('Enter desired end time (YYYY-MM-DD HH:MM:SS): ')
    try:
        desired_start = datetime.datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        desired_end = datetime.datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print('Invalid date format.')
        return

    if desired_end <= desired_start:
        print('End time must be after start time.')
        return

    # Set folder to the directory where the script is located
    folder = os.path.dirname(os.path.abspath(__file__))

    video_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.avi')]

    video_infos = []
    for video_file in video_files:
        start_time = parse_filename(video_file)
        if start_time is None:
            print(f'Cannot parse start time from filename: {video_file}')
            continue
        duration = get_video_duration(video_file)
        if duration is None:
            print(f'Cannot get duration for video: {video_file}')
            continue
        video_infos.append({'filename': video_file, 'start_time': start_time, 'duration': duration})

    if not video_infos:
        print('No valid video files found.')
        return

    # Sort videos by their start times
    video_infos.sort(key=lambda x: x['start_time'])

    # Select videos that overlap with the desired interval
    selected_videos = []
    for info in video_infos:
        video_start = info['start_time']
        video_end = video_start + datetime.timedelta(seconds=info['duration'])
        if video_end <= desired_start or video_start >= desired_end:
            continue  # No overlap
        selected_videos.append(info)

    if not selected_videos:
        print('No videos found overlapping with the desired interval.')
        return

    # Prepare list for concatenation
    output_files = []
    for idx, info in enumerate(selected_videos):
        video_start = info['start_time']
        video_end = video_start + datetime.timedelta(seconds=info['duration'])
        input_file = info['filename']

        # Determine if trimming is needed
        needs_trimming = False
        trim_start = 0
        trim_duration = info['duration']

        if video_start < desired_start and video_end > desired_start:
            # This is the first video and needs trimming at the start
            trim_start = (desired_start - video_start).total_seconds()
            trim_duration = info['duration'] - trim_start
            needs_trimming = True

        if video_start < desired_end and video_end > desired_end:
            # This is the last video and needs trimming at the end
            if not needs_trimming:
                # If it wasn't already marked for trimming (i.e., it's not the first video)
                trim_duration = (desired_end - video_start).total_seconds() - trim_start
                needs_trimming = True
            else:
                # Adjust trim_duration for the first video that also needs trimming at the end
                trim_duration = (desired_end - desired_start).total_seconds()

        if needs_trimming:
            output_file = f'trimmed_{idx}.avi'
            cmd = [
                'ffmpeg', '-y', '-i', input_file,
                '-ss', str(trim_start),
                '-t', str(trim_duration),
                '-an',  # Ignore audio stream
                '-c:v', 'copy',  # Only copy the video stream
                output_file
            ]
            print(f'Trimming video without audio: {input_file}')
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                print(f'Error trimming video: {input_file}')
                continue
            output_files.append(output_file)
        else:
            # No trimming needed; use the original file
            output_files.append(input_file)

    if not output_files:
        print('No videos were added to the final output.')
        return

    # Create a text file listing all the videos to concatenate
    with open('files_to_concat.txt', 'w') as f:
        for output_file in output_files:
            f.write(f"file '{os.path.abspath(output_file)}'\n")

    # Concatenate the videos into one final output, ignoring audio
    final_output = 'final_output_no_audio.avi'
    cmd = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', 'files_to_concat.txt', '-an',  # Ignore audio stream
        '-c:v', 'copy', final_output
    ]
    print('Stitching videos together without audio...')
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print('Error concatenating videos.')
        return

    print(f'Final video saved as {final_output}')

if __name__ == '__main__':
    main()
