from __future__ import unicode_literals
import os
import time
import json
from utils import File
from youtube.utils import constants
from youtube.managers.ffmpeg import Ffmpeg
from utils.File import get_file_name_with_extension, write_lines_to_file_utf8, get_json_data, list_files_sub
from youtube import paths
from youtube.managers.yt_managers import MonitorManager, YoutubeQueueManager, YoutubeDownloader
from youtube.model.yt_queue import YoutubeQueue
from youtube.model.yt_monitors import YoutubeMonitor
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
        result.append(normalize('NFC', line))
        # print(normalize('NFC', line))

    write_lines_to_file_utf8("C:\\Users\\Mefodii\\Downloads\\nfc.txt", result)


def test_file():
    append_to_file("D:\\Automatica\\Python\\PyCharmProjects\\Kevolehc\\Kevolehc\\youtube\\files\\monitors\\DLoaw\\DLoaw.txt",
                   [])


def get_input_data():
    data = []

    for line in stdin:
        if "eoffff" in line:  # If empty string is read then stop the loop
            break
        data.append(line)

    return data


def test_http_ident(data):
    i = 1
    for line in data:
        if "[" in line[1:2]:
            substring = line[115:119]
            if "http" not in substring:
                print(i, line)
        i += 1


def test_json(data):
    monitors = []
    for monitor in data:
        YoutubeMonitor.validate_json(monitor)
        monitors.append(YoutubeMonitor(monitor))

    return ["[", ",\n".join([monitor.to_json() for monitor in monitors]), "]"]


# Create the DB file from already downloaded files
def add_to_db():
    name = "ThePrimeThanatos"
    check_path = "G:\\Music\\" + name
    extension = constants.MP3
    result_path = "D:\\Automatica\\Python\\PyCharmProjects\\Kevolehc\\Kevolehc\\youtube\\files\\_db"
    dbfile = result_path + "\\" + name + ".txt"
    files_list = list_files_sub(check_path)

    result = {}
    for element in files_list:
        abs_path = element["path"] + "\\" + element["filename"]
        if extension == constants.MP4 or extension == constants.MKV:
            if abs_path.endswith(extension):
                metadata = Ffmpeg.metadata_to_json(Ffmpeg.get_metadata(abs_path))
                episode_id = metadata.get("EPISODE_ID", None)
                if episode_id:
                    title = metadata.get("TITLE")
                    track = metadata.get("TRACK")
                    result[episode_id] = {"TITLE": title, "STATUS": "DOWNLOADED", "NUMBER": track,
                                          "CHANNEL_NAME": name, "FILE_NAME": element["filename"], "FORMAT": extension}

        if extension == constants.MP3:
            if abs_path.endswith(extension):
                metadata = Ffmpeg.metadata_to_json(Ffmpeg.get_metadata(abs_path))
                episode_id = metadata.get("DISC", None)
                if episode_id:
                    title = metadata.get("TITLE")
                    track = metadata.get("TRACK")
                    result[episode_id] = {"TITLE": title, "STATUS": "DOWNLOADED", "NUMBER": track,
                                          "CHANNEL_NAME": name, "FILE_NAME": element["filename"], "FORMAT": extension}

    File.write_json_data(dbfile, result)


# Special case: Update ExtraCreditz files metadata from db file
#   Files with track number and without EPISODE_ID will be checked in DB with STATUS=UNABLE
def update_extra_credits():
    db_file = '\\'.join([paths.DB_LOG_PATH, "ExtraCreditz.txt"])
    db_json = File.get_json_data(db_file)
    check_path = "G:\\Filme\\ExtraCreditz"
    files_list = list_files_sub(check_path)

    for element in files_list:
        abs_path = element["path"] + "\\" + element["filename"]
        if abs_path.endswith(constants.MP4):
            metadata = Ffmpeg.metadata_to_json(Ffmpeg.get_metadata(abs_path))
            print(metadata)
            track = int(metadata.get("TRACK", -1))
            episode_id = metadata.get("EPISODE_ID", None)
            if (track > 0) and (episode_id is None):
                for key, value in db_json.items():
                    if value["NUMBER"] == track and value["STATUS"] == "UNABLE":
                        print(key, track)
                        tags = {
                            "episode_id": key
                        }
                        if File.exists(abs_path):
                            Ffmpeg.add_tags(abs_path, tags)

                        value["STATUS"] = "DOWNLOADED"

    File.write_json_data(db_file, db_json)


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    pass

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