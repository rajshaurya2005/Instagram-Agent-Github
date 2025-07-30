import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import re
from config import YOUTUBE_API_KEY

# YouTube API service details
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def parse_duration(duration_str):
    # Parse ISO 8601 duration format (e.g., PT1M30S)
    # This is a simplified parser, a full parser would be more robust
    duration_seconds = 0
    if duration_str and 'PT' in duration_str:
        duration_str = duration_str.replace('PT', '')
        hours = re.search(r'(\d+)H', duration_str)
        minutes = re.search(r'(\d+)M', duration_str)
        seconds = re.search(r'(\d+)S', duration_str)

        if hours: duration_seconds += int(hours.group(1)) * 3600
        if minutes: duration_seconds += int(minutes.group(1)) * 60
        if seconds: duration_seconds += int(seconds.group(1))
    return duration_seconds

def search_youtube(query, k_results, video_type):
    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

        search_params = {
            'q': query,
            'part': 'id,snippet',
            'type': 'video',
            'maxResults': min(k_results, 50),
            'order': 'relevance',
        }

        if video_type == 'shorts':
            search_params['videoDuration'] = 'short'
        elif video_type == 'videos':
            pass

        search_response = youtube.search().list(**search_params).execute()

        video_ids = []
        for search_result in search_response.get('items', []):
            video_ids.append(search_result['id']['videoId'])

        if not video_ids:
            return []

        videos_response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=','.join(video_ids)
        ).execute()

        results = []
        for video_result in videos_response.get('items', []):
            video_id = video_result['id']
            snippet = video_result['snippet']
            content_details = video_result.get('contentDetails', {})

            duration_seconds = parse_duration(content_details.get('duration'))

            is_short_heuristic = duration_seconds > 0 and duration_seconds < 60

            if (video_type == 'shorts' and not is_short_heuristic) or \
               (video_type == 'videos' and is_short_heuristic):
                continue

            results.append({
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'title': snippet.get('title', 'N/A'),
                'thumbnail': snippet['thumbnails']['high']['url'] if 'high' in snippet['thumbnails'] else 'N/A'
            })

        return results[:k_results]

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []