import os
from typing import Tuple
from icecream import ic
from enum import Enum

import googleapiclient.discovery

from utils import File
from ..utils.yt_datetime import compare_yt_dates

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

MAX_RESULTS = 50


class YoutubeVideoItemType(Enum):
    PLAYLIST_ITEM = "PLAYLIST_ITEM"
    VIDEO_ITEM = "VIDEO_ITEM"


class YoutubeVideoItem:
    def __init__(self, data: dict, item_type: YoutubeVideoItemType):
        self.data = data
        self.item_type = item_type

    @staticmethod
    def from_list(data_list: list[dict], item_type: YoutubeVideoItemType):
        return [YoutubeVideoItem(data, item_type) for data in data_list]

    def get_item_publish_date(self) -> str:
        if self.item_type == YoutubeVideoItemType.PLAYLIST_ITEM:
            return self.data.get("contentDetails").get("videoPublishedAt")

        if self.item_type == YoutubeVideoItemType.VIDEO_ITEM:
            return self.data.get("snippet").get("publishedAt")

        raise Exception("Unsupported YoutubeVideoItemType")

    def is_livestream(self) -> bool:
        if self.item_type == YoutubeVideoItemType.VIDEO_ITEM:
            return self.data["snippet"]["liveBroadcastContent"] != "none"

        raise Exception("Unsupported YoutubeVideoItemType")


class YoutubeWorker:

    def __init__(self, dk_file: str):

        self.dk = File.get_file_lines(dk_file)[0]
        self.youtube = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, developerKey=self.dk)

    def get_channel_uploads_playlist_id(self, yt_id: str) -> str:
        request = self.youtube.channels().list(
            part="contentDetails",
            id=yt_id
        )
        response = request.execute()
        uploads_id = response.get("items")[0].get("contentDetails").get("relatedPlaylists").get("uploads")

        return uploads_id

    def get_channel_uploads_from_date(self, yt_id: str, yt_date: str) -> list[dict]:
        uploads_playlist_id = self.get_channel_uploads_playlist_id(yt_id)

        uploads = []
        has_next_page = True
        token = ""
        while has_next_page:
            items, token, has_next_page = self.get_playlist_items(uploads_playlist_id, token)

            for item in items:
                published_at = item.get("contentDetails").get("videoPublishedAt")
                if published_at is not None:
                    if compare_yt_dates(published_at, yt_date) == 1:
                        uploads += [item]
                else:
                    print(f'Warning: ignored video with no publish date \
                            {item.get("snippet").get("resourceId").get("videoId")}')

        uploads = self.remove_livestreams(uploads)
        return uploads

    def remove_livestreams(self, items: list[dict]) -> list[dict]:
        result = []

        ids = [item['contentDetails']['videoId'] for item in items]
        for checked_item, original_item in zip(self.get_videos(ids), items):
            if YoutubeWorker.is_livestream(checked_item):
                print("Livestream to be ignored: " + str(checked_item))
            else:
                result += [original_item]

        if len(result) != len(items):
            print("Some items were ignored. Be cautious")
        return result

    @staticmethod
    def is_livestream(yt_item: dict) -> bool:
        return yt_item["snippet"]["liveBroadcastContent"] != "none"

    def get_videos(self, id_list: list[str]) -> list[dict]:
        items = []

        # Break id_list in arrays of the length of MAX_RESULTS
        chunks = [id_list[i:i + MAX_RESULTS] for i in range(0, len(id_list), MAX_RESULTS)]
        for chunk in chunks:
            comma_chunk = ",".join(chunk)
            request = self.youtube.videos().list(
                part="snippet,liveStreamingDetails,contentDetails",
                id=comma_chunk
            )
            response = request.execute()
            items += response.get('items')

        if len(id_list) != len(items):
            print("Warning: not all videos extracted!")

        return items

    def get_playlist_items(self, playlist_id: str, page_token: str) -> Tuple[dict, str | None, bool]:
        request = self.youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=MAX_RESULTS,
            pageToken=page_token
        )
        response = request.execute()

        token = response.get('nextPageToken')
        has_next_page = True
        if not response.get('items') or not token:
            has_next_page = False

        return response.get('items'), token, has_next_page

    def get_channel_id_from_video(self, video_id: str) -> str:
        item = self.get_videos([video_id])[0]
        ic(item)

        return ""


