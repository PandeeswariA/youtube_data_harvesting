import streamlit as st
import pandas as pd
import pymysql

# Function to execute SQL queries and return results as DataFrame
def execute_query(query):
    conn = pymysql.connect(host='127.0.0.1',
                           user='root',
                           password='password',
                           database='youtube_project')
    with conn.cursor() as cursor:
        cursor.execute(query)
        # Get column names from the result set
        columns = [col[0] for col in cursor.description]
        result = cursor.fetchall()
    conn.close()
    return pd.DataFrame(result), columns

# Main Streamlit app
def main():
    st.title(':red[EXTRACT TRANSFORM]')

    with st.sidebar:
        st.title(":red[Home]")
        st.header(":red[Extract and Upload]")
        st.title(":red[view]")
        
    # Title with larger text size
    st.title("Enter Youtube channel ID below")

    # TextBox
    channel_id = st.text_input("YouTube Channel ID")

    # Button with text "Extract Data"
    if st.button("Extract Data"):
        if channel_id:
            # Perform data extraction based on the provided channel ID
            # from google_api import get_channel_details
            from fetch_channel_data import get_entire_channel_data
            channel_data = get_entire_channel_data(channel_id=channel_id)
            st.write(f"Data extracted for channel ID: {channel_id}")
            st.write(f"Channel Name: {channel_data['ChannelDetails']['channel_name']}")
            
            if 'data' not in st.session_state:
                st.session_state.data = None  
            
            st.session_state.data = channel_data   
            
        else: 
            st.write("Please enter a YouTube Channel ID")

    if st.button("Upload to SQL"):
        channel_data = st.session_state.data
        from insert_channel_data_to_sql import insert_data
        if insert_data(channel_data['ChannelDetails']['channel_id']):
            st.write("Channel Data Inserted Successfully")
        else:
            st.write("Channel Data not Inserted please check error")

    st.header("Select a question to be displayed")
    question = st.selectbox("Select your question",
                               ("1.What are the names of all videos and their corresponding channels ?",
                                "2.Which Channels have the most number of videos and how many videos do they have ?",
                                "3.What are the top 10 most viewed videos and their respective channels ?",
                                "4.How many comments were made on each video and what are their corresponding video names ?",
                                "5.Which video have the highest number of likes and what are their corresponding channel names ?",
                                "6.What is the total number of likes and dislikes for each video and what are their corresponding video names ?",
                                "7.What is the total number of views for each channel and what are their corresponding channel names ?",
                                "8.What are the names of all the channels that have published videos in the year 2022 ?",
                                "9.What is the average duration of all videos in each channel and what are their corresponding channel names ?",
                                "10.Which videos have the highest number of comments and what are their corresponding channel names ?"))
    
    if question:
        # Execute corresponding q uery based on selected question
        if question =="1.What are the names of all videos and their corresponding channels ?":
            query = """
            SELECT v.video_name AS Video_Name, c.channel_name AS Channel_Name
            FROM video v
            INNER JOIN playlist p ON v.playlist_id = p.playlist_id
            INNER JOIN channel c ON p.channel_id = c.channel_id
            """
        elif question =="2.Which Channels have the most number of videos and how many videos do they have ?":
            query = """
            SELECT c.channel_name AS Channel_Name, COUNT(v.video_id) AS Num_Videos
            FROM video v
            INNER JOIN playlist p ON v.playlist_id = p.playlist_id
            INNER JOIN channel c ON p.channel_id = c.channel_id
            GROUP BY c.channel_id
            ORDER BY Num_Videos DESC
            LIMIT 1
            """
        elif question =="3.What are the top 10 most viewed videos and their respective channels ?":
            query = """
            SELECT v.video_name AS Video_Name, c.channel_name AS Channel_Name, v.view_count AS View_Count
            FROM video v
            INNER JOIN playlist p ON v.playlist_id = p.playlist_id
            INNER JOIN channel c ON p.channel_id = c.channel_id
            ORDER BY v.view_count DESC
            LIMIT 10
            """
        elif question =="4.How many comments were made on each video and what are their corresponding video names ?":
            query = """
            SELECT v.video_name AS Video_Name, COUNT(cm.comment_id) AS Num_Comments
            FROM video v
            LEFT JOIN comment cm ON v.video_id = cm.video_id
            GROUP BY v.video_id
            """
        elif question =="5.Which video have the highest number of likes and what are their corresponding channel names ?":
            query = """
            SELECT v.video_name AS Video_Name, c.channel_name AS Channel_Name, v.like_count AS Like_Count
            FROM video v
            INNER JOIN playlist p ON v.playlist_id = p.playlist_id
            INNER JOIN channel c ON p.channel_id = c.channel_id
            ORDER BY v.like_count DESC
            LIMIT 1
            """
        elif question =="6.What is the total number of likes and dislikes for each video and what are their corresponding video names ?":
            query = """
            SELECT v.video_name AS Video_Name, SUM(v.like_count) AS Total_Likes, SUM(v.dislike_count) AS Total_Dislikes
            FROM video v
            GROUP BY v.video_id
            """
        elif question == "7.What is the total number of views for each channel and what are their corresponding channel names ?":
            query = """
            SELECT c.channel_name AS Channel_Name, SUM(v.view_count) AS Total_Views
            FROM video v
            INNER JOIN playlist p ON v.playlist_id = p.playlist_id
            INNER JOIN channel c ON p.channel_id = c.channel_id
            GROUP BY c.channel_id
            """
        elif question =="8.What are the names of all the channels that have published videos in the year 2022 ?":
            query = """
            SELECT DISTINCT c.channel_name AS Channel_Name
            FROM channel c
            INNER JOIN playlist p ON c.channel_id = p.channel_id
            INNER JOIN video v ON p.playlist_id = v.playlist_id
            WHERE YEAR(v.published_date) = '2022'
            """
        elif question =="9.What is the average duration of all videos in each channel and what are their corresponding channel names ?":
            query = """
            SELECT c.channel_name AS Channel_Name, AVG(v.duration) AS Avg_Duration
            FROM video v
            INNER JOIN playlist p ON v.playlist_id = p.playlist_id
            INNER JOIN channel c ON p.channel_id = c.channel_id
            GROUP BY c.channel_id
            """
        elif question =="10.Which videos have the highest number of comments and what are their corresponding channel names ?":
            query = """
            SELECT v.video_name AS Video_Name, c.channel_name AS Channel_Name, COUNT(cm.comment_id) AS Num_Comments
            FROM video v
            INNER JOIN playlist p ON v.playlist_id = p.playlist_id
            INNER JOIN channel c ON p.channel_id = c.channel_id
            LEFT JOIN comment cm ON v.video_id = cm.video_id
            GROUP BY v.video_id
            ORDER BY Num_Comments DESC
            LIMIT 1
            """
        
        # Execute the query and display results as DataFrame
        df, columns = execute_query(query)
        st.subheader(question)
        df.columns = columns  # Rename DataFrame columns with actual column names
        st.dataframe(df)

if __name__ == '__main__':
    main()
