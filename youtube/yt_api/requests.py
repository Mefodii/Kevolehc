import os
import googleapiclient.discovery

from utils import File

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
api_service_name = "youtube"
api_version = "v3"

MAX_RESULTS = 50


class YoutubeWorker():
    def __init__(self, dk_file):

        self.dk = File.get_file_lines(dk_file)[0]
        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=self.dk)

    def get_channel_id_from_name(self, yt_name):
        request = self.youtube.channels().list(
            part="id",
            forUsername=yt_name
        )
        return request.execute()

    def get_channel_videos_from_date2(self, yt_id, yt_date):
        request = self.youtube.search().list(
            part="snippet,id",
            channelId=yt_id,
            maxResults=MAX_RESULTS,
            order="date",
            publishedAfter=yt_date,
            pageToken=""
        )

        return request.execute()

    def get_channel_videos_from_date(self, yt_id, yt_date):
        items = []
        next_page = True
        token = ""
        while next_page:
            request = self.youtube.search().list(
                part="snippet,id",
                channelId=yt_id,
                maxResults=MAX_RESULTS,
                order="date",
                publishedAfter=yt_date,
                pageToken=token
            )
            response = request.execute()
            print(response)
            items += response.get('items')
            token = response.get('nextPageToken')
            if not response.get('items') or not token:
                next_page = False

        return items
