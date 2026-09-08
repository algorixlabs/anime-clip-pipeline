import os
import re
import sys
import subprocess
from typing import Tuple
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """Enforce strict HTTP/HTTPS schemes to prevent protocol injection."""
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def parse_timestamp_to_seconds(ts: str) -> int:
    """Convert HH:MM:SS, MM:SS, or SS into integer seconds."""
    parts = list(map(int, ts.strip().split(":")))
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] if len(parts) == 1 else -1


def is_valid_timestamp(ts: str) -> bool:
    """Validate format and verify minutes/seconds are under 60."""
    pattern = r"^(\d{1,2}:){0,2}\d{1,2}$"
    if not re.match(pattern, ts.strip()):
        return False
    parts = list(map(int, ts.strip().split(":")))
    return not (len(parts) > 1 and any(p >= 60 for p in parts[1:]))


def download_clip(url: str, start: str, end: str, output_name: str = "final_clip.mp4") -> bool:
    """Executes yt-dlp safely with option-injection guards and process timeouts."""
    print("\n[+] Initializing stream cut...")
    safe_output = os.path.basename(output_name.strip())
    
    # '--' explicitly stops flag parsing to eliminate option injection
    command = [
        "yt-dlp",
        "-S", "res:720,ext:mp4:m4a",
        "--download-sections", f"*{start}-{end}",
        "--force-keyframes-at-cuts",
        "-o", safe_output,
        "--",
        url
    ]
    
    try:
        subprocess.run(command, check=True, timeout=300)
        print(f"\n[✓] Clip successfully saved as: {safe_output}")
        return True
    except subprocess.TimeoutExpired:
        print("\n[!] Process timed out after 5 minutes.")
        return False
    except subprocess.CalledProcessError:
        print("\n[!] Download failed. Verify the URL, timestamps, or network connection.")
        return False
    except FileNotFoundError:
        print("\n[!] Error: 'yt-dlp' executable not found. Run 'pip install yt-dlp'.")
        return False


def collect_inputs() -> Tuple[str, str, str]:
    """Collects and validates inputs from interactive CLI."""
    print("=" * 36)
    print("   ANIME CLIP AUTOMATION PIPELINE   ")
    print("=" * 36)
    
    while True:
        video_url = input("\nEnter YouTube URL: ").strip()
        if is_valid_url(video_url):
            break
        print("[!] Invalid URL. Must start with http:// or https://")
        
    while True:
        start_time = input("Enter start timestamp (HH:MM:SS or MM:SS): ").strip()
        if is_valid_timestamp(start_time):
            break
        print("[!] Invalid format/range. Minutes and seconds must be under 60.")
        
    while True:
        end_time = input("Enter end timestamp (HH:MM:SS or MM:SS): ").strip()
        if is_valid_timestamp(end_time):
            if parse_timestamp_to_seconds(end_time) > parse_timestamp_to_seconds(start_time):
                break
            print("[!] End time must be greater than start time.")
        else:
            print("[!] Invalid format/range.")
            
    return video_url, start_time, end_time


def main():
    try:
        url, start, end = collect_inputs()
        print(f"\n--- Processing Job ---\nURL: {url}\nStart: {start}\nEnd: {end}")
        download_clip(url, start, end)
    except KeyboardInterrupt:
        print("\n\n[!] Operation cancelled by user. Exiting cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    main()

