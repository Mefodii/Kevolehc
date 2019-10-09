from __future__ import unicode_literals
import os
import time
from youtube.managers.ffmpeg import Ffmpeg
from utils.File import get_file_name_with_extension
from youtube import paths
from youtube.managers.yt_managers import MonitorManager, YoutubeQueueManager, YoutubeDownloader
from youtube.model.yt_queue import YoutubeQueue
from youtube.yt_api.requests import YoutubeWorker
from youtube_dl.utils import DownloadError
from youtube.utils.yt_datetime import yt_to_py
from utils.File import append_to_file
from unicodedata import normalize
from sys import stdin

def download():
    queue = YoutubeQueue("Sh0djQG5eEI", "test", paths.YOUTUBE_RESULT_PATH, "mp3")
    try:
        YoutubeDownloader.download(queue)
    except DownloadError:
        print("meh")


def test_yt_to_py():
    a = yt_to_py("2019-06-04T06:16:06.816Z")
    b = yt_to_py("2019-06-04T06:16:06.816Z")
    c = yt_to_py("2019-06-04T06:16:06.817Z")
    d = yt_to_py("2019-06-04T06:16:06.815Z")
    e = yt_to_py("2019-06-04T06:16:05.816Z")
    f = yt_to_py("2019-06-04T06:15:06.816Z")

    print(a == b)
    print(a == c)
    print(a == d)
    print(a < b)
    print(a > f)


def test_tags():
    file_abs_path = "D:\\Automatica\\Python\\PyCharmProjects\\Kevolehc\\Kevolehc\\youtube\\" \
                    "files\\monitors\\ThePrimeThanatos" \
                    "\\1.mp3"
                    # "\\677 - ThePrimeThanatos - 'Back To The 80's' _ Best of Synthwave And Retro Electro Music Mix _ Vol. 21.mp3"

    tags = {
        "genre": "ThePrimeThanatos",
        "title": "'Back To The 80's | Best of Synthwave And Retro Electro Music Mix | Vol. 21",
        "track": "677",
        "copyright": "ThePrimeThanatos",
        "disc": "1Ny7vnWdoLc",
        "comment": "by Mefodii"
    }

    print(file_abs_path)
    print(tags)

    Ffmpeg.add_tags(file_abs_path, tags)


def test_compose_unicode(data):
    result = []

    for line in data:
        print(normalize('NFC', line))


def test_file():
    append_to_file("D:\\Automatica\\Python\\PyCharmProjects\\Kevolehc\\Kevolehc\\youtube\\files\\monitors\\DLoaw\\DLoaw.txt",
                   [])


def get_input_data():
    data = []

    for line in stdin:
        if "eof" in line:  # If empty string is read then stop the loop
            break
        data.append(line)

    return data


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    test_compose_unicode(get_input_data())

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