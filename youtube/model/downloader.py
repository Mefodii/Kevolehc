import copy
# import youtube_dl  # <-- Use this to downlaod from bandcamp (2022.08.13 - It still worked)
import yt_dlp as youtube_dl
# For VK downloads use yt-dlp==2021.11.10

from utils import File

from .yt_queue import YoutubeQueue
from ..utils import constants
from ..managers.ffmpeg import Ffmpeg
from ..utils.constants import ALLOWED_VIDEO_QUALITY

DL_EXTENSION = "ext"
DL_TITLE = "title"


class YoutubeDownloaderLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


class YoutubeDownloader:

    def __init__(self, ffmpeg_location):
        self.ffmpeg_location = ffmpeg_location
        # Stats received after download is finished, from the hook
        self.download_stats = None

    def my_hook(self, d):
        if d['status'] == 'finished':
            self.download_stats = d

    def download(self, queue: YoutubeQueue):
        if queue.save_format == constants.MP3:
            self.download_audio(queue)
        elif queue.save_format == constants.MKV or queue.save_format == constants.MP4:
            self.download_video(queue)
        else:
            print("Handling not supported for extension " + queue.save_format)

    def download_audio(self, queue: YoutubeQueue):
        output_file_path = queue.save_location + '\\' + queue.file_name + '.%(ext)s'
        ydl_opts = self.build_audio_download_options(output_file_path)

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([queue.link])

            result = ydl.extract_info("{}".format(queue.link))
            queue.audio_dl_stats = copy.deepcopy(self.download_stats)

    def download_video(self, queue: YoutubeQueue):
        # TODO: delete audio/video parts if exists
        # Validate video_quality value
        video_quality = queue.video_quality
        if video_quality and video_quality not in ALLOWED_VIDEO_QUALITY:
            raise Exception(
                f"Video quality option not found in allowed values. Received value: {video_quality}\n"
                f"Allowed values: {ALLOWED_VIDEO_QUALITY}")

        # Download audio part
        default_audio_name = "audio"
        audio_file = queue.save_location + "\\" + default_audio_name
        output_file_path = audio_file + '.%(ext)s'
        ydl_opts = self.build_audio_fragment_download_options(output_file_path)
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([queue.link])
            result = ydl.extract_info("{}".format(queue.link), download=False)
            queue.audio_dl_stats = copy.deepcopy(self.download_stats)

        # Download video part (has no sound)
        default_video_name = "video"
        video_file = queue.save_location + "\\" + default_video_name
        output_file_path = video_file + '.%(ext)s'
        ydl_opts = self.build_video_fragment_download_options(output_file_path)
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([queue.link])
            result = ydl.extract_info("{}".format(queue.link), download=False)
            queue.video_dl_stats = copy.deepcopy(self.download_stats)

        # Replace tags from file_name by its values from queue.video_dl_stats
        queue.replace_file_name_tags()

        # Merge audio and video parts to single file
        audio_file = default_audio_name + "." + constants.M4A
        video_file_extension = File.get_file_name_with_extension(queue.save_location, default_video_name).split(".")[-1]
        video_file = default_video_name + "." + video_file_extension

        merged_file = queue.file_name + "." + queue.save_format
        Ffmpeg.merge_audio_and_video(queue.save_location, audio_file, video_file, merged_file)

        if video_quality:
            print(f"Resizing video file to: {video_quality}")
            Ffmpeg.resize(f"{queue.save_location}\\{merged_file}", height=video_quality)

    def build_common_download_options(self, output_file_path):
        return {
            'ffmpeg_location': self.ffmpeg_location,
            'outtmpl': output_file_path,
            'logger': YoutubeDownloaderLogger(),
            'progress_hooks': [self.my_hook]
        }

    def build_audio_download_options(self, output_file_path):
        options = self.build_common_download_options(output_file_path)
        options['format'] = 'bestaudio/best'
        options['cachedir'] = False
        options['postprocessors'] = [{'key': 'FFmpegExtractAudio',
                                      'preferredcodec': 'mp3',
                                      'preferredquality': '192'}]
        return options

    def build_audio_fragment_download_options(self, output_file_path):
        options = self.build_common_download_options(output_file_path)
        options['format'] = 'bestaudio/best'
        options['cachedir'] = False
        options['postprocessors'] = [{'key': 'FFmpegExtractAudio',
                                      'preferredcodec': 'm4a',
                                      'preferredquality': '192'},
                                     {'key': 'FFmpegMetadata'}]
        return options

    def build_video_fragment_download_options(self, output_file_path):
        options = self.build_common_download_options(output_file_path)
        options['format'] = 'bestvideo/best'
        options['no-cache-dir'] = True
        return options
