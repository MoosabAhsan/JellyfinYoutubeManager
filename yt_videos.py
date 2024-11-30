import json
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Initialize YouTube API client
def get_youtube_client(api_key):
    return build('youtube', 'v3', developerKey=api_key)


# Load channels from a JSON file
def load_channels(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return {channel['id']: channel['name'] for channel in data.get('channels', [])}

# Load search prompts from a JSON file
def load_search_prompts(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('search_prompts', [])

# Get videos posted in the last week from a specific channel
def get_videos_from_last_week(youtube, channel_id):
    one_week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat("T") + "Z"
    
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        publishedAfter=one_week_ago,
        maxResults=10,
        order='date',
        type='video'
    )
    response = request.execute()
    return response['items']

# Get videos based on search prompts
def get_videos_from_search_prompts(youtube, prompt, max_results):
    one_week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat("T") + "Z"
    
    request = youtube.search().list(
        part='snippet',
        q=prompt,
        publishedAfter=one_week_ago,
        maxResults=max_results,
        order='viewCount',  # Order by view count
        type='video'
    )
    response = request.execute()
    return response['items']

# Get video details including duration
def get_video_details(youtube, video_ids):
    request = youtube.videos().list(
        part='contentDetails',
        id=','.join(video_ids)
    )
    response = request.execute()
    return response['items']

# Convert ISO 8601 duration to total seconds
def iso8601_to_seconds(iso_duration):
    import isodate  # Make sure you have isodate installed
    duration = isodate.parse_duration(iso_duration)
    return int(duration.total_seconds())

def main():
    api_key = 'REDACTED'  # Replace with your YouTube API key
    youtube = get_youtube_client(api_key)

    # Load channels from a JSON file
    channels = load_channels('channels.json')
    
    total_duration_seconds = 0  # Initialize total duration

    for channel_id, channel_name in channels.items():
        print(f"Fetching videos from channel: {channel_id}")
        videos = get_videos_from_last_week(youtube, channel_id)
        
        video_ids = []
        # Debugging output: Print the video titles and channel names
        for video in videos:
            channel_name = video['snippet']['channelTitle']  # Get channel name
            video_ids.append(video['id']['videoId'])  # Store video ID
            print(f"Video title: {video['snippet']['title']} (Channel: {channel_name})")

        # Get video details for duration
        if video_ids:
            video_details = get_video_details(youtube, video_ids)
            for detail in video_details:
                duration = detail['contentDetails']['duration']  # Get duration
                duration_seconds = iso8601_to_seconds(duration)  # Convert to seconds
                total_duration_seconds += duration_seconds  # Sum durations

  

    # Convert total duration from seconds to hours
    total_duration_hours = total_duration_seconds / 3600
    print(f"\nTotal duration of all videos found: {total_duration_hours:.2f} hours")

if __name__ == "__main__":
    main()
