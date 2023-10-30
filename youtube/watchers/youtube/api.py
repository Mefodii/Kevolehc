import os
import re
from typing import Tuple
from icecream import ic
from enum import Enum

import googleapiclient.discovery

from utils import File
from youtube.utils.yt_datetime import compare_yt_dates

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

MAX_RESULTS = 50
MAX_DURATION = 21600  # 6 hours


class YoutubeAPIVideoType(Enum):
    PLAYLIST_ITEM = "PLAYLIST_ITEM"
    VIDEO_ITEM = "VIDEO_ITEM"


class YoutubeAPIVideo:
    def __init__(self, data: dict, item_type: YoutubeAPIVideoType):
        self.data = data
        self.item_type = item_type

    @staticmethod
    def from_list(data_list: list[dict], item_type: YoutubeAPIVideoType):
        return [YoutubeAPIVideo(data, item_type) for data in data_list]

    @staticmethod
    def sort_by_publish_date(items):
        return sorted(items, key=lambda k: k.get_publish_date())

    def get_id(self):
        if self.item_type == YoutubeAPIVideoType.PLAYLIST_ITEM:
            return self.data.get("snippet").get("resourceId").get("videoId")
        if self.item_type == YoutubeAPIVideoType.VIDEO_ITEM:
            return self.data["id"]

        raise Exception(f"Unsupported YoutubeVideoItemType: {self.item_type}")

    def get_channel_name(self):
        if self.item_type == YoutubeAPIVideoType.PLAYLIST_ITEM:
            return self.data.get("snippet").get("channelTitle")

        raise Exception(f"Unsupported YoutubeVideoItemType: {self.item_type}")

    def get_title(self):
        if self.item_type == YoutubeAPIVideoType.PLAYLIST_ITEM:
            return self.data.get("snippet").get("title")
        if self.item_type == YoutubeAPIVideoType.VIDEO_ITEM:
            return self.data.get("snippet").get("title")

        raise Exception(f"Unsupported YoutubeVideoItemType: {self.item_type}")

    def get_publish_date(self) -> str:
        if self.item_type == YoutubeAPIVideoType.PLAYLIST_ITEM:
            return self.data.get("contentDetails").get("videoPublishedAt")

        if self.item_type == YoutubeAPIVideoType.VIDEO_ITEM:
            return self.data.get("snippet").get("publishedAt")

        raise Exception(f"Unsupported YoutubeVideoItemType: {self.item_type}")

    def is_livestream(self) -> bool:
        if self.item_type == YoutubeAPIVideoType.VIDEO_ITEM:
            return self.data["snippet"]["liveBroadcastContent"] != "none"

        raise Exception(f"Unsupported YoutubeVideoItemType: {self.item_type}")

    def has_valid_duration(self) -> bool:
        return 0 < self.get_duration_seconds() <= MAX_DURATION

    def is_video_kind(self):
        if self.item_type == YoutubeAPIVideoType.PLAYLIST_ITEM:
            return self.data.get("snippet").get("resourceId").get("kind") == "youtube#video"

        raise Exception(f"Unsupported YoutubeVideoItemType: {self.item_type}")

    def get_channel_id(self) -> str:
        if self.item_type == YoutubeAPIVideoType.VIDEO_ITEM:
            return self.data["snippet"]["channelId"]

        raise Exception(f"Unsupported YoutubeVideoItemType: {self.item_type}")

    def get_duration(self) -> str:
        if self.item_type == YoutubeAPIVideoType.VIDEO_ITEM:
            return self.data["contentDetails"]["duration"]

        raise Exception(f"Unsupported YoutubeVideoItemType: {self.item_type}")

    def get_duration_seconds(self) -> int:
        duration_str = self.get_duration()

        days = re.search(r"\d*D", duration_str)
        hours = re.search(r"\d*H", duration_str)
        minutes = re.search(r"\d*M", duration_str)
        seconds = re.search(r"\d*S", duration_str)

        total_seconds = 0
        if days:
            total_seconds += int(days.group()[:-1]) * 86400
        if hours:
            total_seconds += int(hours.group()[:-1]) * 3600
        if minutes:
            total_seconds += int(minutes.group()[:-1]) * 60
        if seconds:
            total_seconds += int(seconds.group()[:-1])

        return total_seconds

    def __repr__(self):
        return f"{self.item_type.__repr__()}, {self.data.__repr__()}"


class YoutubeWorker:

    def __init__(self, dk_file: str):

        self.dk = File.read(dk_file)[0]
        self.youtube = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, developerKey=self.dk)

    def get_channel_uploads_playlist_id(self, yt_id: str) -> str:
        """
        Each YouTube channel has a default "uploads" playlist which contains all the videos
        :param yt_id: IF of the YouTube channel
        :return: ID of the playlist named "uploads"
        """
        request = self.youtube.channels().list(
            part="contentDetails",
            id=yt_id
        )
        response = request.execute()
        uploads_id = response.get("items")[0].get("contentDetails").get("relatedPlaylists").get("uploads")

        return uploads_id

    def get_channel_uploads_from_date(self, yt_id: str, yt_date: str) -> list[YoutubeAPIVideo]:
        """
        :param yt_id:
        :param yt_date:
        :return: uploads for given YouTube id in ascending order strictly later than yt_date
        """
        uploads_playlist_id = self.get_channel_uploads_playlist_id(yt_id)

        uploads: list[YoutubeAPIVideo] = []
        has_next_page = True
        token = ""
        reached_yt_date = False
        while has_next_page and not reached_yt_date:
            items, token, has_next_page = self.get_playlist_items(uploads_playlist_id, token)

            for item in items:
                published_at = item.get_publish_date()
                if published_at is not None:
                    if compare_yt_dates(published_at, yt_date) == 1:
                        uploads += [item]
                    else:
                        reached_yt_date = True
                else:
                    print(f'Warning: ignored video with no publish date {item.get_id()}')

        uploads = self.remove_livestreams(uploads)
        result = uploads[::-1]

        # Note 2023.10.17: a check to be sure that results is still received in
        #  chronological order and API is working as usual
        sorted_uploads = YoutubeAPIVideo.sort_by_publish_date(uploads)
        for i1, i2 in zip(sorted_uploads, result):
            if i1 != i2:
                ic(i1, i2)

        return result

    def remove_livestreams(self, items: list[YoutubeAPIVideo]) -> list[YoutubeAPIVideo]:
        result = []

        ids = [item.get_id() for item in items]
        for checked_item, original_item in zip(self.get_videos(ids), items):
            if checked_item.is_livestream():
                print(f"Livestream to be ignored: {checked_item}")
            elif not checked_item.has_valid_duration():
                print(f"Item has no valid duration: {checked_item.get_duration()}. Item: {checked_item}")
            else:
                result += [original_item]

        if len(result) != len(items):
            print("Some items were ignored. Be cautious")

        return result

    def get_videos(self, id_list: list[str]) -> list[YoutubeAPIVideo]:
        items: list[YoutubeAPIVideo] = []

        # Breaks id_list in arrays of the length of MAX_RESULTS
        chunks = [id_list[i:i + MAX_RESULTS] for i in range(0, len(id_list), MAX_RESULTS)]
        for chunk in chunks:
            comma_chunk = ",".join(chunk)
            request = self.youtube.videos().list(
                part="snippet,liveStreamingDetails,contentDetails",
                id=comma_chunk
            )
            response = request.execute()
            items += YoutubeAPIVideo.from_list(response.get('items'), YoutubeAPIVideoType.VIDEO_ITEM)

        if len(id_list) != len(items):
            print("Warning: not all videos extracted!")

        return items

    def get_playlist_items(self, playlist_id: str, page_token: str) -> Tuple[list[YoutubeAPIVideo], str | None, bool]:
        # Note 2023.10.17: It seems that results are sorted by publish date

        request = self.youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=MAX_RESULTS,
            pageToken=page_token
        )
        response = request.execute()
        token = response.get('nextPageToken')
        has_next_page = True
        items = YoutubeAPIVideo.from_list(response.get('items'), YoutubeAPIVideoType.PLAYLIST_ITEM)

        if not items or not token:
            has_next_page = False

        return items, token, has_next_page

    def get_channel_id_from_video(self, video_id: str) -> str:
        item = self.get_videos([video_id])[0]
        return item.get_channel_id()


