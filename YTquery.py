# -*- coding: utf-8 -*-

import pprint as pp
import csv
import unidecode
import googleapiclient.discovery
import datetime
import re
import pprint

channel_list = []
channel_list_byID = []

#IMPORTING CHANNEL LIST FROM .TXT FILE
try:
    with open('channel_list.txt', 'r') as file:
        for line in file:
            if line.endswith('\n'):
                line = line[:-1]
            
            channel_list.append(line)
except:
    pass

try:
    with open('channel_list_ID.txt', 'r') as file2:
        for line in file2:
            if line.endswith('\n'):
                line = line[:-1]

            channel_list_byID.append(line)
except:
    pass

#API KEY ACCREDITATION
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyCn5vJlv3gvO3pDSBbTJn55JCzrRi33AfM"
#Alternative DEVELOPER KEY for work  AIzaSyCQqMzFVZGqAapmOaScbWLqYQUlr2TIAkc
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)

#PREPARES A DICTIONARY WITH CHANNEL NAMES AS KEYS AND FULL CHANNEL DATA AS VALUES
def preparing_playlists():
    
    channel_data_dict = {}
    for channel in channel_list:
        channel_request = youtube.channels().list(
            part = 'contentDetails, statistics',
            forUsername = channel,
            )
      
        channel_response = channel_request.execute()
        channel_data = channel_response.get('items', [])
        
        channel_playlist = channel_data[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        channel_data_dict.update({channel: channel_data})
    
    return channel_data_dict

def preparing_playlists_byID():
    channel_data_dict_byID = {}

    for channel in channel_list_byID:
        channel_request = youtube.channels().list(
            part = 'contentDetails, statistics',
            id = channel,
            )
      
        channel_response = channel_request.execute()
        channel_data = channel_response.get('items', [])
        
        channel_playlist = channel_data[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        channel_data_dict_byID.update({channel: channel_data})

    return channel_data_dict_byID

def adding_dictionaries(By_name, By_ID):
    By_name.update(By_ID)
    return By_name

#REQUESTS DATA FOR EACH VIDEO FROM 
def getting_videos(arg):
    channel_data_dict = arg
    CurrentDate_text = str(datetime.date.today())
    csvFile_byChannel = open('{}_byChannel.csv'.format(CurrentDate_text),'w', newline = '')
    csvWriter_byChannel = csv.writer(csvFile_byChannel)
    csvWriter_byChannel.writerow(['channel_name', 'channel_sub_count', 'sum_of_views', 'sum_of_likes', 'sum_of_dislikes', 'sum_of_comments', 'sum_of_videos'])    
    csvFile_byVideo = open('{}_byVideo.csv'.format(CurrentDate_text),'w', newline = '')
    csvWriter_byVideo = csv.writer(csvFile_byVideo)
    csvWriter_byVideo.writerow(['title', 'channel_title', 'viewCount', 'date_of_publishing', 'likeCount', 'dislikeCount', 'commentCount'])
    for item in channel_data_dict:
        channel_playlist = channel_data_dict[item][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        channel_name = item
        channel_sub_count = channel_data_dict[item][0]['statistics']['subscriberCount']
        
    
        playlist_request = youtube.playlistItems().list(
            part = "snippet",
            maxResults = 50,
            playlistId= channel_playlist
        )

        playlist_response = playlist_request.execute()

        sum_of_views = 0
        sum_of_likes = 0
        sum_of_dislikes = 0
        sum_of_comments = 0
        sum_of_videos = 0
          
        for playlist_item in playlist_response.get("items", []):
            
            video_Published_at = datetime.datetime.strptime(playlist_item["snippet"]['publishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
            video_Id = playlist_item["snippet"]["resourceId"]['videoId']
            channel_title = playlist_item["snippet"]["channelTitle"]
            
            CurrentDate = datetime.datetime.now()
            time_delta = CurrentDate - video_Published_at
            
            if time_delta > datetime.timedelta(days=7) and time_delta < datetime.timedelta(days=365):
                matured_video = video_Id

                m_video_request = youtube.videos().list(
                    part = "snippet, statistics",
                    id = matured_video
                    )
                video_ID_number = matured_video

                m_video_response = m_video_request.execute()

                for video_data in m_video_response.get("items", []):
                    video_Title = video_data["snippet"]["title"]
                    title = unidecode.unidecode(video_Title)
                    channel_title = video_data["snippet"]["channelTitle"]
                    date_of_publishing = video_data["snippet"]["publishedAt"]
                    viewCount = video_data["statistics"]["viewCount"]
                    if 'likeCount' not in video_data["statistics"]:
                        likeCount = 0
                    else:
                        likeCount = video_data["statistics"]["likeCount"]
                        
                    if 'dislikeCount' not in video_data["statistics"]:
                        dislikeCount = 0
                    else:
                        dislikeCount = video_data["statistics"]["dislikeCount"]
                        
                    if 'commentCount' not in video_data["statistics"]:
                        commentCount = 0
                    else:
                        commentCount = video_data["statistics"]["commentCount"]

                    sum_of_views += int(viewCount)
                    sum_of_likes += int(likeCount)
                    sum_of_dislikes += int(dislikeCount)
                    sum_of_comments += int(commentCount)
                    sum_of_videos += 1
                csvWriter_byVideo.writerow([title, channel_title, viewCount, date_of_publishing, likeCount, dislikeCount, commentCount])
        csvWriter_byChannel.writerow([channel_title, channel_sub_count, sum_of_views, sum_of_likes, sum_of_dislikes, sum_of_comments, sum_of_videos])

    csvFile_byVideo.close()
    csvFile_byChannel.close()        

if __name__ == "__main__":
    try:
        channel_data = preparing_playlists()
        channel_data2 = preparing_playlists_byID()
        final_dictionary = adding_dictionaries(channel_data, channel_data2)
        pp.pprint(final_dictionary)
        getting_videos(final_dictionary)
    except:
        pass
