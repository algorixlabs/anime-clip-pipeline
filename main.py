import re

def is_valid_timestamp(ts):
    # Validates HH:MM:SS, MM:SS, or SS formats
    pattern = r"^(\d{1,2}:)?(\d{1,2}:)?\d{1,2}$"
    return bool(re.match(pattern, ts.strip()))

def get_user_input():
    print("=== Anime Clip Automation ===")
    
    video_url = input("Enter the video URL: ").strip()
    while not video_url:
        video_url = input("URL cannot be empty. Enter video URL: ").strip()
        
    start_time = input("Enter start timestamp (HH:MM:SS or MM:SS): ").strip()
    while not is_valid_timestamp(start_time):
        start_time = input("Invalid format! Enter start timestamp (e.g. 00:01:30): ").strip()
        
    end_time = input("Enter end timestamp (HH:MM:SS or MM:SS): ").strip()
    while not is_valid_timestamp(end_time):
        end_time = input("Invalid format! Enter end timestamp (e.g. 00:01:45): ").strip()
        
    print("\n--- Validated Job Summary ---")
    print(f"Target URL: {video_url}")
    print(f"Start: {start_time}")
    print(f"End: {end_time}")

if __name__ == "__main__":
    get_user_input()

