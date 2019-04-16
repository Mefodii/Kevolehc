import os
import googleapiclient.discovery

from utils import File

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
api_service_name = "youtube"
api_version = "v3"


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

    def get_channel_videos_from_date(self, yt_id, yt_date):
        request = self.youtube.search().list(
            part="snippet,id",
            channelId=yt_id,
            maxResults=100,
            order="date"
        )

        return request.execute()