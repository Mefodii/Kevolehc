from __future__ import unicode_literals
import os
import time
import youtube_dl
from youtube import paths
from utils import File


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


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    to_download = File.get_file_lines('/'.join([paths.INPUT_FILES_PATH, paths.YOUTUBE_INPUT_FILE]))
    i = 1
    for youtube_link in to_download:
        ydl_opts = {
            'format': 'bestaudio/best',
            'add-metadata': True,
            'ffmpeg_location': paths.RESOURCES_PATH,
            'outtmpl': paths.YOUTUBE_RESULT_PATH + '/' + str(i) + ' - %(title)s''.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192'},
                                {'key': 'MetadataFromTitle',
                                'titleformat': '(?P<artist>.+)\ \-\ (?P<title>.+)'},
                                {'key': 'FFmpegMetadata'}],
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_link])
        i += 1


#######################################################################################################################
# Process
#######################################################################################################################
if __name__ == "__main__":
    # Start time of the program
    start = time.time()

    # Main functionality
    __main__()

    # End time of the program
    end = time.time()
    # Running time of the program
    print("Program ran for: ", end - start, "seconds.")