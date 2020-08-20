from __future__ import unicode_literals
import os
import time
import sys
import traceback
import youtube_dl
from youtube import paths
from youtube.settings.settings import YTDownloadSettings
from youtube.utils import constants
from utils import File
from youtube.managers.ffmpeg import Ffmpeg
from youtube.utils.file_names import replace_restricted_file_chars

DEFAULT_SETTINGS = "settings.json"


def process_my_location():
    abs_path = repr(sys.argv[0])[1:-1]

    split_by = "/"
    if "\\" in abs_path:
        split_by = "\\"

    return "\\".join(abs_path.split(split_by)[0:-1])


MY_LOCATION = process_my_location()


def download(link, ext):
    if ext == constants.MP3:
        download_audio(link)
    if ext == constants.MKV or ext == constants.MP4:
        download_video(link, ext)


def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'ffmpeg_location': paths.RESOURCES_PATH,
        'outtmpl': paths.YOUTUBE_RESULT_PATH + '/%(title)s''.%(ext)s',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'postprocessors': [{'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192'}],
        'cachedir': False,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])


def download_video(link, ext):
    default_audio_name = "audio"
    default_video_name = "video"
    audio_file = paths.YOUTUBE_RESULT_PATH + "\\" + default_audio_name
    video_file = paths.YOUTUBE_RESULT_PATH + "\\" + default_video_name

    ydl_opts = {
        'format': 'bestaudio/best',
        'ffmpeg_location': paths.RESOURCES_PATH,
        'outtmpl': audio_file + '.%(ext)s',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'postprocessors': [{'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'm4a',
                            'preferredquality': '192'},
                           {'key': 'FFmpegMetadata'}],
        'cachedir': False,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

    ydl_opts = {
        'format': 'bestvideo/best',
        'ffmpeg_location': paths.RESOURCES_PATH,
        'outtmpl': video_file + '.%(ext)s',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'no-cache-dir': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
        result = ydl.extract_info("{}".format(link))
        ydl.prepare_filename(result)
        title = replace_restricted_file_chars(result["title"])

    audio_file = default_audio_name + "." + constants.M4A

    video_file_extension = File.get_file_name_with_extension(paths.YOUTUBE_RESULT_PATH, default_video_name).split(".")[-1]
    video_file = default_video_name + "." + video_file_extension
    merged_file = title + "." + ext

    Ffmpeg.merge_audio_and_video(paths.YOUTUBE_RESULT_PATH, audio_file, video_file, merged_file)


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def print_traceback():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
    traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)
    traceback.print_exc()
    formatted_lines = traceback.format_exc().splitlines()
    print(formatted_lines[0])
    print(formatted_lines[-1])
    print(repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))
    print(repr(traceback.extract_tb(exc_traceback)))
    print(repr(traceback.format_tb(exc_traceback)))


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__(settings_file):
    os.chdir(MY_LOCATION)
    print("Started at: " + MY_LOCATION)
    if settings_file:
        settings = YTDownloadSettings(settings_file)

        input_file = '/'.join([MY_LOCATION, settings.input_file])
        output_directory = '/'.join([MY_LOCATION, settings.output_directory])
        resources_path = '/'.join([MY_LOCATION, settings.resources_path])
    else:
        input_file = '/'.join([paths.INPUT_FILES_PATH, paths.YOUTUBE_INPUT_FILE])
        output_directory = paths.YOUTUBE_RESULT_PATH
        resources_path = paths.RESOURCES_PATH

    download_data = File.get_file_lines(input_file)
    i = 1
    for data_line in download_data:
        # ext, link = data_line.split(";")
        ydl_opts = {
            'format': 'bestaudio/best',
            # 'add-metadata': True,
            'ffmpeg_location': resources_path,
            # 'outtmpl': paths.YOUTUBE_RESULT_PATH + '/' + str(i) + ' - %(title)s''.%(ext)s',
            'outtmpl': output_directory + '/%(title)s''.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192'},],
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
            'cachedir': False,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # ydl.cache.remove()
            ydl.download([data_line])
        # download(link, ext)
        i += 1


#######################################################################################################################
# Process
#######################################################################################################################
if __name__ == "__main__":
    # Start time of the program
    start = time.time()

    # print(File.get_json_data("C:\\Users\\Mefodii\\Downloads\\YoutubeDownloader\\settings.json"))
    # Main functionality
    try:
        args = sys.argv

        if len(args) > 1:
            if args[1] == "local":
                __main__(None)
            else:
                print("Argument not valid")
        else:
            __main__(DEFAULT_SETTINGS)
    except:
        print_traceback()
        input("Press enter to end")
        raise

    # End time of the program
    end = time.time()
    # Running time of the program
    print("Program ran for: ", end - start, "seconds.")