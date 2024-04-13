from googleapiclient.errors import HttpError

import googleapiclient.discovery
import googleapiclient.errors
import json

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
api=""

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"

# Get credentials and create an API client
youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api)

def get_channel_information(channel_id=""):
    request = youtube.channels().list(part="snippet,contentDetails,statistics",
                                      id=channel_id)

    channel_data = request.execute()

    channel_informations = {
    'channel_id': channel_id,
    'channel_name' : channel_data['items'][0]['snippet']['title'],
    'channel_description' : channel_data['items'][0]['snippet']['description'],
    'playlists' : channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
    }

    return channel_informations

def get_playlist_data(channel_information={}):
    playlist_information = {
    'playlist_id' : channel_information["ChannelDetails"]['playlists'],
    'channel_id'  : channel_information["ChannelDetails"]['channel_id'], 
    'playlist_name' : channel_information["ChannelDetails"]['playlists']
    }
    return playlist_information
    

def get_videos_list(playlist_id=""):
    videos_list=[]
    try:
        playlist_items = []
        next_page_token = None
        while True:
            playlist_request = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,  # Maximum number of results per page
                pageToken=next_page_token
            )
            playlist_response = playlist_request.execute()
            playlist_items.extend(playlist_response['items'])
            
            # Check if there are more pages
            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break

        # Print titles and video IDs of the videos in the playlist
        for item in playlist_items:
            videos_list.append(item['snippet']['resourceId']['videoId'])
        return videos_list

    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
    except Exception as e:
        print(f'An error occurred: {str(e)}')

    return videos_list

def duration_to_seconds(duration):
    # Extract the time part from the duration string
    time_str = duration[2:]

    # Initialize variables to store hours, minutes, and seconds
    hours, minutes, seconds = 0, 0, 0

    # Split the time string into components
    parts = time_str.split('H')
    if len(parts) == 2:
        hours = int(parts[0])
        time_str = parts[1]

    parts = time_str.split('M')
    if len(parts) == 2:
        minutes = int(parts[0])
        time_str = parts[1]

    parts = time_str.split('S')
    if len(parts) == 2:
        seconds = int(parts[0])

    # Calculate total duration in seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds

    return total_seconds

def get_entire_channel_data(channel_id=""):
    entire_channel_data = {}
    entire_channel_data["ChannelDetails"] = get_channel_information(channel_id=channel_id)

    playlist_data = get_playlist_data(entire_channel_data)
    entire_channel_data["PlayList"] = playlist_data
    entire_channel_data["Videos"] = {}

    # for video_id in get_videos_list(channel_id):
    for video_id in get_videos_list(entire_channel_data["ChannelDetails"]["playlists"]):
        try:
            video_request = youtube.videos().list(part="snippet,contentDetails,statistics",
                                    id=video_id)
            video_response = video_request.execute()

            if video_response['items']:
                video_information = {
                    "Video_Id": video_id,
                    "Playlist_Id": playlist_data["playlist_id"],
                    "Video_Name": video_response['items'][0]['snippet']['title'] if 'title' in video_response['items'][0]['snippet'] else "Not Available",
                    "Video_Description": video_response['items'][0]['snippet']['description'],
                    "Published_Date": video_response['items'][0]['snippet']['publishedAt'],
                    "View_Count": int(video_response['items'][0]['statistics']["viewCount"]),
                    "Like_Count": int(video_response['items'][0]['statistics']["likeCount"]),
                    "Favorite_Count": int(video_response['items'][0]['statistics']["favoriteCount"]), 
                    "DisLike_Count": 0,
                    "Comment_Count": int(video_response['items'][0]['statistics']["commentCount"]),
                    "Duration": duration_to_seconds(video_response['items'][0]['contentDetails']["duration"]),
                    "Thumbnail": video_response['items'][0]['snippet']["thumbnails"]["default"]["url"],
                    "Captain_Status": video_response['items'][0]['contentDetails']["caption"]
                }
    
                comments = {}
                next_page_token = None
                while True:
                    comments_request = youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        maxResults=100,  # Maximum number of results per page
                        pageToken=next_page_token
                    )
                    comments_response = comments_request.execute()

                    for comment in comments_response['items']:
                        comment_id = comment['snippet']['topLevelComment']['id']
                        comment_information = {
                        "Comment_Id": comment['snippet']['topLevelComment']['id'],
                        "Comment_Text": comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                        "Comment_Author": comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        "Comment_PublishedAt": comment['snippet']['topLevelComment']['snippet']['publishedAt']
                        }
                        comments[comment_id] = comment_information
                    
                    # Check if there are more pages
                    next_page_token = comments_response.get('nextPageToken')
                    if not next_page_token:
                        break
                video_information['Comments'] = comments
                entire_channel_data["Videos"][video_id] = video_information

        except HttpError as e:
            print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
            continue
        except Exception as e:
            print(f'An error occurred: {str(e)}')
            continue

    file_path = channel_id + ".json"
    with open(file_path, 'w') as json_file:
        json.dump(entire_channel_data, json_file, indent=4)

    return entire_channel_data

