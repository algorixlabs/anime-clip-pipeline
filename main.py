import os
import re
import sys
import shutil
import subprocess
from datetime import datetime
from typing import Tuple
from urllib.parse import urlparse

# Target Android storage directory
DESTINATION_DIR = os.path.expanduser("~/storage/shared/Movies/AnimeClips")


def is_valid_url(url: str) -> bool:
    """Enforce HTTP/HTTPS schemes to prevent local protocol injection."""
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def parse_timestamp_to_seconds(ts: str) -> int:
    """Convert HH:MM:SS or MM:SS into integer seconds."""
    parts = list(map(int, ts.strip().split(":")))
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] if len(parts) == 1 else -1


def is_valid_timestamp(ts: str) -> bool:
    """Validate format bounds and ensure seconds/minutes are valid."""
    pattern = r"^(\d{1,2}:){0,2}\d{1,2}$"
    if not re.match(pattern, ts.strip()):
        return False
    parts = list(map(int, ts.strip().split(":")))
    return not (len(parts) > 1 and any(p >= 60 for p in parts[1:]))


def generate_filename() -> str:
    """Generate a clean, unique timestamped filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"anime_clip_{timestamp}.mp4"


def route_file_to_gallery(temp_filepath: str, filename: str) -> str:
    """Move processed video to Android storage and trigger MediaStore indexing."""
    try:
        os.makedirs(DESTINATION_DIR, exist_ok=True)
        target_path = os.path.join(DESTINATION_DIR, filename)
        shutil.move(temp_filepath, target_path)
        
        # Get the real Android path (resolving the Termux symlink)
        real_path = os.path.realpath(target_path)
        
        # Tell Android MediaStore to index the new file for Gallery apps
        subprocess.run(
            [
                "am", "broadcast",
                "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
                "-d", f"file://{real_path}"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return target_path
    except PermissionError:
        print("\n[!] Storage permission denied. Run 'termux-setup-storage'.")
        return ""
    except Exception as e:
        print(f"\n[!] File routing error: {e}")
        return ""


def download_clip(url: str, start: str, end: str) -> bool:
    """Execute stream cut and route file to destination directory."""
    filename = generate_filename()
    temp_filepath = os.path.join(os.getcwd(), filename)
    
    print("\n[+] Extracting video stream...")
    
    command = [
        "yt-dlp",
        "-S", "res:720,ext:mp4:m4a",
        "--download-sections", f"*{start}-{end}",
        "--force-keyframes-at-cuts",
        "-o", temp_filepath,
        "--",
        url
    ]
    
    try:
        subprocess.run(command, check=True, timeout=300)
        print(f"[✓] Stream extracted successfully.")
        
        final_path = route_file_to_gallery(temp_filepath, filename)
        if final_path:
            print(f"[✓] Clip saved to phone gallery:\n    {final_path}")
            return True
        return False
        
    except subprocess.TimeoutExpired:
        print("\n[!] Operation timed out after 5 minutes.")
        return False
    except subprocess.CalledProcessError:
        print("\n[!] Download failed. Check network or video availability.")
        return False
    except FileNotFoundError:
        print("\n[!] 'yt-dlp' executable missing. Run 'pip install yt-dlp'.")
        return False


def collect_inputs() -> Tuple[str, str, str]:
    """Gather and validate interactive CLI inputs."""
    print("=" * 40)
    print("   ANIME CLIP AUTOMATION PIPELINE (v1.0)   ")
    print("=" * 40)
    
    while True:
        video_url = input("\nEnter YouTube URL: ").strip()
        if is_valid_url(video_url):
            break
        print("[!] Invalid URL scheme. Must start with http:// or https://")
        
    while True:
        start_time = input("Enter start timestamp (HH:MM:SS or MM:SS): ").strip()
        if is_valid_timestamp(start_time):
            break
        print("[!] Invalid timestamp format or range.")
        
    while True:
        end_time = input("Enter end timestamp (HH:MM:SS or MM:SS): ").strip()
        if is_valid_timestamp(end_time):
            if parse_timestamp_to_seconds(end_time) > parse_timestamp_to_seconds(start_time):
                break
            print("[!] End time must be greater than start time.")
        else:
            print("[!] Invalid timestamp format or range.")
            
    return video_url, start_time, end_time


def main():
    try:
        url, start, end = collect_inputs()
        print(f"\n--- Job Confirmation ---\nURL:   {url}\nStart: {start}\nEnd:   {end}")
        download_clip(url, start, end)
    except KeyboardInterrupt:
        print("\n\n[!] Script stopped by user. Exiting cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    main()

