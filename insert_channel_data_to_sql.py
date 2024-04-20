import json
import pymysql
from datetime import datetime

def read_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def insert_channel(cursor, channel_details):
    cursor.execute('''
        INSERT INTO channel (channel_id, channel_name, channel_description)
        VALUES (%s, %s, %s)
    ''', (channel_details['channel_id'], channel_details['channel_name'], channel_details['channel_description']))

def insert_playlist(cursor, playlist_details):
    cursor.execute('''
        INSERT INTO playlist (playlist_id, channel_id, playlist_name)
        VALUES (%s, %s, %s)
    ''', (playlist_details['playlist_id'], playlist_details['channel_id'], playlist_details['playlist_name']))

def insert_video(cursor, video_info):
    cursor.execute('''
        INSERT INTO video (video_id, playlist_id, video_name, video_description, published_date, view_count,
                           like_count, dislike_count, favorite_count, comment_count, duration, thumbnail, caption_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (video_info['Video_Id'], video_info['Playlist_Id'], video_info['Video_Name'], video_info['Video_Description'],
          datetime.strptime(video_info['Published_Date'], '%Y-%m-%dT%H:%M:%SZ'), video_info.get('View_Count', 0),
          video_info.get('Like_Count', 0), video_info.get('DisLike_Count', 0), video_info.get('Favorite_Count', 0),
          video_info.get('Comment_Count', 0), video_info.get('Duration', 0), video_info.get('Thumbnail', ''),
          video_info.get('Caption_Status', '')))

def insert_comments(cursor, comments, video_id):
    for comment_info in comments.values():
        cursor.execute('''
            INSERT INTO comment (comment_id, video_id, comment_text, comment_author, comment_published_date)
            VALUES (%s, %s, %s, %s, %s)
        ''', (comment_info['Comment_Id'], video_id, comment_info['Comment_Text'], comment_info['Comment_Author'],
              datetime.strptime(comment_info['Comment_PublishedAt'], '%Y-%m-%dT%H:%M:%SZ')))

def insert_data(channel_id):
    # Connect to MySQL database
    try:
        connection = pymysql.connect(host="127.0.0.1",
                                    user="root",
                                    password="password",
                                    database="youtube_project")
        cursor = connection.cursor()

        # Read JSON data
        data = read_json(channel_id + '.json')

        # Insert data into tables
        insert_channel(cursor, data['ChannelDetails'])
        insert_playlist(cursor, data['PlayList'])

        # playlist_id = data['PlayList']['playlist_id']
        for video_id, video_info in data['Videos'].items():
            # print("Video ID", video_id)
            # print("Playlist ID",playlist_id)
            insert_video(cursor, video_info)
            comments = video_info.get('Comments')
            if comments:
                insert_comments(cursor, comments, video_id)
        connection.commit()
        connection.close()
        print("Channel Data Inserted Successfully")
        return True
    except Exception as e:
        print("Exception {0}".format(e))
        return False