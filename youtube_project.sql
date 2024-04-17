create database youtube_project;
use youtube_project;
 
create table channel (
	channel_id varchar(255) primary key,
    channel_name varchar(255),
    channel_type varchar(255),
    channel_views int,
    channel_description text,
    channel_status varchar(255)
);

create table playlist (
	playlist_id varchar(255) primary key,
	channel_id varchar(255),
    playlist_name varchar(255),
	FOREIGN KEY(channel_id) REFERENCES channel(channel_id)
);
    
create table video (
	video_id varchar(255) primary key,
    playlist_id varchar(255),
    video_name varchar(255),
    video_description text,
    published_date datetime,
    view_count int,
    like_count int,
    dislike_count int,
    favorite_count int,
    comment_count int,
    duration varchar(20),
    thumbnail varchar(255),
    caption_status varchar(255),
    foreign key (playlist_id) references playlist(playlist_id)
);

create table comment (
	comment_id varchar(255) unique,
    video_id varchar(255),
    comment_text text,
    comment_author varchar(100),
    comment_published_date datetime,
    foreign key (video_id) references video(video_id)
);

select *from channel;
select *from playlist;
select *from video;
select *from comment;