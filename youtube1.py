# Import necessary libraries
from googleapiclient.discovery import build
import pymongo
from datetime import datetime, timedelta

# Define API credentials and parameters
API_KEY = 'AIzaSyAX0WBz3m3kDwHrEh25gOrPmeYWUIUlSWo'
CHANNEL_ID = 'UC1234567890'
MAX_RESULTS = 50 # maximum number of results per API request
PUBLISHED_AFTER = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ') # only retrieve videos published in the past week
FIELDS = 'items(id,snippet(publishedAt,channelId,title,description,thumbnails,tags),statistics)'

# Connect to MongoDB
#client = pymongo.MongoClient("mongodb+srv://kk:123@cluster0.le0owl3.mongodb.net/test?retryWrites=true&w=majority")
client = pymongo.MongoClient(
    "mongodb+srv://kk:123@cluster0.le0owl3.mongodb.net/test?retryWrites=true&w=majority&dns=8.8.8.8",
    connectTimeoutMS=300000,
    socketTimeoutMS=None,
    serverSelectionTimeoutMS=500000,
)

db = client['youtube']
collection = db['videos']

# Retrieve videos from API and insert into MongoDB
youtube = build('youtube', 'v3', developerKey=API_KEY)
nextPageToken = ''
while True:
    request = youtube.search().list(part='id', channelId=CHANNEL_ID, maxResults=MAX_RESULTS, publishedAfter=PUBLISHED_AFTER, type='video', pageToken=nextPageToken)
    response = request.execute()
    videoIds = [item['id']['videoId'] for item in response['items']]
    if not videoIds:
        break
    videoRequest = youtube.videos().list(part=FIELDS, id=','.join(videoIds))
    videoResponse = videoRequest.execute()
    for item in videoResponse['items']:
        video = {
            'videoId': item['id'],
            'publishedAt': item['snippet']['publishedAt'],
            'channelId': item['snippet']['channelId'],
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'thumbnails': item['snippet']['thumbnails'],
            'tags': item['snippet'].get('tags', []),
            'viewCount': item['statistics']['viewCount'],
            'likeCount': item['statistics']['likeCount'],
            'dislikeCount': item['statistics']['dislikeCount'],
            'favoriteCount': item['statistics']['favoriteCount'],
            'commentCount': item['statistics']['commentCount']
        }
        collection.insert_one(video)
    if 'nextPageToken' in response:
        nextPageToken = response['nextPageToken']
    else:
        break
