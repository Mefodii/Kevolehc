from ..utils import constants
from .. import paths

from utils import File
from ..managers.ffmpeg import Ffmpeg

import youtube_dl


def build_common_download_options(output_file_path):
    return {
            'ffmpeg_location': paths.RESOURCES_PATH,
            'outtmpl': output_file_path,
            'logger': YoutubeDownloaderLogger(),
            'progress_hooks': [YoutubeDownloader.my_hook]
            }


def get_audio_download_options(output_file_path):
    options = build_common_download_options(output_file_path)
    options['format'] = 'bestaudio/best'
    options['cachedir'] = False
    options['postprocessors'] = [{'key': 'FFmpegExtractAudio',
                                         'preferredcodec': 'mp3',
                                         'preferredquality': '192'}]
    return options


def get_audio_fragment_download_options(output_file_path):
    options = build_common_download_options(output_file_path)
    options['format'] = 'bestaudio/best'
    options['cachedir'] = False
    options['postprocessors'] = [{'key': 'FFmpegExtractAudio',
                                  'preferredcodec': 'm4a',
                                  'preferredquality': '192'},
                                 {'key': 'FFmpegMetadata'}]
    return options


def get_video_fragment_download_options(output_file_path):
    options = build_common_download_options(output_file_path)
    options['format'] = 'bestvideo/best'
    options['no-cache-dir'] = True
    return options


class YoutubeDownloaderLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


class YoutubeDownloader:

    @staticmethod
    def my_hook(d):
        pass

    @staticmethod
    def download(queue):
        if queue.save_format == constants.MP3:
            YoutubeDownloader.download_audio(queue)
        if queue.save_format == constants.MKV or queue.save_format == constants.MP4:
            YoutubeDownloader.download_video(queue)

    @staticmethod
    def download_audio(queue):
        output_file_path = queue.save_location + '\\' + queue.file_name + '.%(ext)s'
        ydl_opts = get_audio_download_options(output_file_path)

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([queue.link])

    @staticmethod
    def download_video(queue):
        default_audio_name = "audio"
        default_video_name = "video"
        audio_file = queue.save_location + "\\" + default_audio_name
        video_file = queue.save_location + "\\" + default_video_name

        output_file_path = audio_file + '.%(ext)s'
        ydl_opts = get_audio_fragment_download_options(output_file_path)

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([queue.link])

        output_file_path = video_file + '.%(ext)s'
        ydl_opts = get_video_fragment_download_options(output_file_path)

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([queue.link])

        audio_file = default_audio_name + "." + constants.M4A

        video_file_extension = File.get_file_name_with_extension(queue.save_location, default_video_name).split(".")[-1]
        video_file = default_video_name + "." + video_file_extension
        merged_file = queue.file_name + "." + queue.save_format

        Ffmpeg.merge_audio_and_video(queue.save_location, audio_file, video_file, merged_file)
