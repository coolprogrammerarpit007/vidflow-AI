import ffmpeg
import os

def stitch_videos(video_paths: list[str], output_path: str) -> bool:
    """
    Takes a list of local video file paths and seamlessly concatenates them 
    into a single output video using FFmpeg.
    
    Args:
        video_paths (list[str]): A list of relative paths to the video chunks (e.g., ["static/videos/chunk1.mp4", ...])
        output_path (str): The relative path where the final video should be saved.
        
    Returns:
        bool: True if successful, raises an Exception otherwise.
    """
    try:
        # 1. Create a text file listing all videos (required by FFmpeg's concat demuxer)
        list_file_path = "static/videos/concat_list.txt"
        
        with open(list_file_path, 'w') as f:
            for path in video_paths:
                # FFmpeg is strict about path formatting. We must use forward slashes, 
                # even on Windows, and adjust the relative path to point correctly.
                safe_path = path.replace('\\', '/')
                # Because the command runs from the root backend directory, 
                # we just need to prefix it with a relative indicator
                f.write(f"file '../../{safe_path}'\n")

        # 2. Run FFmpeg to concatenate
        print(f"Stitching {len(video_paths)} videos into {output_path}...")
        
        (
            ffmpeg
            .input(list_file_path, format='concat', safe=0)
            # c='copy' is crucial: it merges the files directly without re-encoding,
            # saving immense CPU power and time.
            .output(output_path, c='copy') 
            .run(overwrite_output=True, quiet=True)
        )

        # 3. Clean up the temporary text file to keep the directory tidy
        if os.path.exists(list_file_path):
            os.remove(list_file_path)

        return True

    except ffmpeg.Error as e:
        # If FFmpeg crashes, this decodes the actual error message from the C-binary
        error_message = e.stderr.decode() if e.stderr else str(e)
        print(f"FFmpeg Error: {error_message}")
        
        # Ensure we still clean up the text file even if it fails
        if os.path.exists("static/videos/concat_list.txt"):
            os.remove("static/videos/concat_list.txt")
            
        raise Exception(f"Video stitching failed: {error_message}")