
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

def home_page():
    st.title(":blue[YOUTUBE DATA HARVESTING and WAREHOUSING USING SQLand STREAMLIT]")
    st.subheader(":blue[DOMAIN :]")
    st.write("social media")
    st.subheader(":blue[Skills take away from this project  :]")
    st.write("Python scripting, API integration, data collection, Data Management using SQL, STREAMLIT")
    st.subheader(":blue[Library used in Python : ]")
    st.write("Google API Client, Streamlit, pymyql, pandas, datetime, json, httperror")  
    st.subheader(":blue[Overall View :]")
    st.write("This project include data extraction from YouTube using youtube data API , Collected Data are uploading  into SQL  database using pymysql python library, after data are uploaded to SQL successfully, The user can perform several SQL queries about youtube channel and the result of query are visualized using pandas python library in Streamlit app ")

    
def extract_page():
    st.title(":blue[Extract Data from Youtube]")
    st.write("The Users can input a YouTube channel ID into a text box and click a Extract Data button to extract data related to channel information like channel_details, playlist_details, video_deatails and comments details etc,. This all details are fetched using Youtube Data API ")

    st.title(':red[EXTRACT TRANSFORM]')

    st.header("Enter Youtube channel ID below")

    # TextBox
    channel_id = st.text_input("YouTube Channel ID")

    # Button with text "Extract Data"
    if st.button("Extract Data"):
        if channel_id:
            # Perform data extraction based on the provided channel ID
            from fetch_channel_data import get_entire_channel_data
            channel_data = get_entire_channel_data(channel_id=channel_id)
            st.write(f"Data extracted for channel ID: {channel_id}")
            st.write(f"Channel Name: {channel_data['ChannelDetails']['channel_name']}")
            
            if 'data' not in st.session_state:
                st.session_state.data = None  
            
            st.session_state.data = channel_data   
            
        else: 
            st.write("Please enter a YouTube Channel ID")

       
def upload_page():
    st.title(":blue[Upload Data to SQL :]")
    st.write("This extracted data are uploaded into SQL database using pymysql python library")

    if st.button("Upload to SQL"):
        channel_data = st.session_state.data
        from insert_channel_data_to_sql import insert_data
        if insert_data(channel_data['ChannelDetails']['channel_id']):
            st.write("Channel Data Inserted Successfully")
        else:
            st.write("Channel Data not Inserted please check error")

def view_page():
    st.title(":blue[Query to be Performed by User :]")
    st.write("The User can perform the following query and get the results as a pandas dataframe.")
    st.title("SQL Query")
    st.subheader("Select a question to be displayed")
    
    queries = {
    "1. What are the names of all videos and their corresponding channels?": """
        SELECT v.video_name AS Video_Name, c.channel_name AS Channel_Name
        FROM video v
        INNER JOIN playlist p ON v.playlist_id = p.playlist_id
        INNER JOIN channel c ON p.channel_id = c.channel_id
    """,
    "2. Which Channels have the most number of videos and how many videos do they have?": """
        SELECT c.channel_name AS Channel_Name, COUNT(v.video_id) AS Num_Videos
        FROM video v
        INNER JOIN playlist p ON v.playlist_id = p.playlist_id
        INNER JOIN channel c ON p.channel_id = c.channel_id
        GROUP BY c.channel_id
        ORDER BY Num_Videos DESC
        LIMIT 1
    """,
    "3. What are the top 10 most viewed videos and their respective channels?": """
        SELECT v.video_name AS Video_Name, c.channel_name AS Channel_Name, v.view_count AS View_Count
        FROM video v
        INNER JOIN playlist p ON v.playlist_id = p.playlist_id
        INNER JOIN channel c ON p.channel_id = c.channel_id
        ORDER BY v.view_count DESC
        LIMIT 10
    """,
    "4. How many comments were made on each video and what are their corresponding video names?": """
        SELECT v.video_name AS Video_Name, COUNT(cm.comment_id) AS Num_Comments
        FROM video v
        LEFT JOIN comment cm ON v.video_id = cm.video_id
        GROUP BY v.video_id
    """,
    "5. Which video has the highest number of likes and what is its corresponding channel name?": """
        SELECT v.video_name AS Video_Name, c.channel_name AS Channel_Name, v.like_count AS Like_Count
        FROM video v
        INNER JOIN playlist p ON v.playlist_id = p.playlist_id
        INNER JOIN channel c ON p.channel_id = c.channel_id
        ORDER BY v.like_count DESC
        LIMIT 1
    """,
    "6. What is the total number of likes and dislikes for each video and what are their corresponding video names?": """
        SELECT v.video_name AS Video_Name, SUM(v.like_count) AS Total_Likes, SUM(v.dislike_count) AS Total_Dislikes
        FROM video v
        GROUP BY v.video_id
    """,
    "7. What is the total number of views for each channel and what are their corresponding channel names?": """
        SELECT c.channel_name AS Channel_Name, SUM(v.view_count) AS Total_Views
        FROM video v
        INNER JOIN playlist p ON v.playlist_id = p.playlist_id
        INNER JOIN channel c ON p.channel_id = c.channel_id
        GROUP BY c.channel_id
    """,
    "8. What are the names of all the channels that have published videos in the year 2022?": """
        SELECT DISTINCT c.channel_name AS Channel_Name
        FROM channel c
        INNER JOIN playlist p ON c.channel_id = p.channel_id
        INNER JOIN video v ON p.playlist_id = v.playlist_id
        WHERE YEAR(v.published_date) = '2022'
    """,
    "9. What is the average duration of all videos in each channel and what are their corresponding channel names?": """
        SELECT c.channel_name AS Channel_Name, AVG(v.duration) AS Avg_Duration
        FROM video v
        INNER JOIN playlist p ON v.playlist_id = p.playlist_id
        INNER JOIN channel c ON p.channel_id = c.channel_id
        GROUP BY c.channel_id
    """,
    "10. Which videos have the highest number of comments and what are their corresponding channel names?": """
        SELECT v.video_name AS Video_Name, c.channel_name AS Channel_Name, COUNT(cm.comment_id) AS Num_Comments
        FROM video v
        INNER JOIN playlist p ON v.playlist_id = p.playlist_id
        INNER JOIN channel c ON p.channel_id = c.channel_id
        LEFT JOIN comment cm ON v.video_id = cm.video_id
        GROUP BY v.video_id
        ORDER BY Num_Comments DESC
        LIMIT 1
    """
}
    
    selected_query = st.selectbox("Select your question", list(queries.keys()))

    # Button to view the answer
    if st.button("View Answer"):
        if selected_query in queries:
            query = queries[selected_query]
            df, columns = execute_query(query)
            df.columns = columns  # Rename DataFrame columns with actual column names
            st.subheader(selected_query)
            st.dataframe(df)
        else:
            st.error("Selected query not found.")

def main():
    st.sidebar.title(":red[EXTRACT and TRANSFORM]")
    page = st.sidebar.radio("Select Page", ("Home Page", "Extract Page", "Upload Page", "View Page"))

    if page == "Home Page":
        home_page()
    elif page == "Extract Page":
        extract_page()
    elif page == "Upload Page":
        upload_page()
    elif page == "View Page":
        view_page()
                
if __name__ == '__main__':
    main()
