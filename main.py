import re
import subprocess

def is_valid_timestamp(ts):
    pattern = r"^(\d{1,2}:)?(\d{1,2}:)?\d{1,2}$"
    return bool(re.match(pattern, ts.strip()))

def download_clip(url, start, end):
    print("\n>>> Starting the cut...")
    
    # We build the exact terminal command as a list of strings
    command = [
        "yt-dlp",
        "-S", "res:720,ext:mp4:m4a",
        "--download-sections", f"*{start}-{end}",
        "--force-keyframes-at-cuts",
        "-o", "final_clip.mp4",
        url
    ]
    
    # This tells Python to press "Enter" on that command
    subprocess.run(command)
    print("\n>>> Clip saved as final_clip.mp4!")

def get_user_input():
    print("=== Anime Clip Automation ===")
    
    video_url = input("Enter the video URL: ").strip()
    while not video_url:
        video_url = input("URL cannot be empty. Enter video URL: ").strip()
        
    start_time = input("Enter start timestamp (HH:MM:SS or MM:SS): ").strip()
    while not is_valid_timestamp(start_time):
        start_time = input("Invalid format! Enter start: ").strip()
        
    end_time = input("Enter end timestamp (HH:MM:SS or MM:SS): ").strip()
    while not is_valid_timestamp(end_time):
        end_time = input("Invalid format! Enter end: ").strip()
        
    print("\n--- Validated Job Summary ---")
    print(f"Target URL: {video_url}")
    print(f"Start: {start_time}")
    print(f"End: {end_time}")
    
    # Trigger the download using the validated inputs
    download_clip(video_url, start_time, end_time)

if __name__ == "__main__":
    get_user_input()

