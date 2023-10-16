from __future__ import unicode_literals
import os
import time
import json

import googleapiclient
from icecream import ic

from utils import File
from youtube.utils import constants
from youtube.managers.ffmpeg import Ffmpeg
from utils.File import get_file_name_with_extension, write_lines_to_file_utf8, get_json_data, list_files_sub, \
    append_to_file
from youtube import paths
from youtube.managers.yt_managers import MonitorManager, YoutubeQueueManager, YoutubeDownloader
from youtube.model.yt_queue import YoutubeQueue
from youtube.model.yt_monitors import YoutubeMonitor
from youtube.model.yt_video import YoutubeVideo
from youtube.utils.file_names import replace_unicode_chars
from youtube.yt_api.requests import YoutubeWorker
from youtube_dl.utils import DownloadError
from youtube.utils.yt_datetime import yt_to_py
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
    file_abs_path = "E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\" \
                    "files\\monitors\\GameChops" \
                    "\\605 - GameChops - Undertale Remix - Arcien - Heartache (from _Hopes & Dreams_) - GameChops.mp3"
    # "\\1053 - Extra Credits - ♫ Policing London - _Alleyways & Truncheons_ - Extra History Music.mp4"
    # "\\677 - ThePrimeThanatos - 'Back To The 80's' _ Best of Synthwave And Retro Electro Music Mix _ Vol. 21.mp3"

    if file_abs_path.endswith(constants.MP3):
        tags = {
            "genre": "GameChops",
            # "title": "'Back To The 80's | Best of Synthwave And Retro Electro Music Mix | Vol. 21",
            "title": "Undertale & Remix - Arcien - & Heartache (from \"Hopes & ss & Dreams\")  & \" - GameChops \" zz \" &",
            "track": "605",
            "comment": "by Mefodii"
        }
    else:
        tags = {
            "author": "ExtraCreditz",
            "title": "♫ Policing London - \"Alleyways & Truncheons\" - Extra History Music",
            "track": str(1053),
            "copyright": "ExtraCreditz",
            "episode_id": "EO_16t_Fe5s",
            "comment": "by Mefodii"
        }

    print(file_abs_path)
    print(tags)
    print(File.exists(file_abs_path))

    Ffmpeg.add_tags(file_abs_path, tags)


def test_compose_unicode(data):
    result = []

    composed = False
    for line in data:
        normalized = normalize('NFC', line)
        result.append(normalized[:-1])
        if not normalized == line:
            composed = True

    print(composed)
    write_lines_to_file_utf8("C:\\Users\\Mefodii\\Downloads\\nfc.txt", result)


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
    result_path = "E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\_db"
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


#  Add to position 168 track number if does not exist
def add_track_number_to_txt_list(data, db_json):
    output_line = ""
    for line2 in data:
        line = line2[:-1]
        if "[" in line[1:2]:
            substring = line[115:119]
            if "http" not in substring:
                print("ERROR:", line)
                exit()

            yt_id = line[147:158]
            db_rec = db_json.get(yt_id, None)
            if not db_rec:
                print("ERROR:", yt_id)
                exit()

            if len(line) < 168:
                output_line = line.ljust(167) + str(db_rec["NUMBER"])
            else:
                output_line = line
        else:
            output_line = line

        print(output_line)


def test_download_videos(links_json):
    video_list = []
    q_list = []
    name = "CriticalRole" # https://criticalrole.fandom.com/wiki/List_of_episodes
    format = constants.MKV
    output_directory = paths.YOUTUBE_RESULT_PATH

    data = {}
    for item in links_json:
        item_id = item["LINK"][32:]
        item_nr = item["TRACK"]
        data[item_id] = item_nr

    dk_file = '/'.join([paths.INPUT_FILES_PATH, paths.YOUTUBE_DK_FILE])
    worker = YoutubeWorker(dk_file)
    videos = worker.get_videos(list(data.keys()))

    for item in videos:
        print(item)
        yt_video_params = YoutubeVideo.parse_json_yt_response(item)
        yt_video = YoutubeVideo(yt_video_params[YoutubeVideo.ID], yt_video_params[YoutubeVideo.TITLE],
                                yt_video_params[YoutubeVideo.PUBLISHED_AT],
                                yt_video_params[YoutubeVideo.CHANNEL_NAME], data.get(yt_video_params[YoutubeVideo.ID]))
        video_list.append(yt_video)

    for video in video_list:
        file_name = " - ".join([str(video.number), name, str(video.title)])
        save_location = output_directory

        queue = YoutubeQueue(video.id, file_name, save_location, format)
        print(repr(queue))

        video.file_name = queue.file_name
        video.save_location = queue.save_location

        q_list.append(queue)

    q_len = str(len(q_list))
    i = 0
    downloader = YoutubeDownloader(paths.RESOURCES_PATH)
    for queue in q_list:
        i += 1
        q_progress = str(i) + "/" + q_len

        result_file = queue.save_location + "\\" + queue.file_name + "." + queue.save_format
        if File.exists(result_file):
            print("Queue ignored, file exist: " + q_progress)
        else:
            print("Process queue: " + q_progress + " - " + result_file)
            try:
                downloader.download(queue)
            except DownloadError:
                print("Unable to download - " + queue.link)

    for video in video_list:
        file_extension = format
        file_abs_path = "\\".join([video.save_location, video.file_name]) + "." + file_extension

        tags = {
            "author": name,
            "title": video.title,
            "track": str(video.number),
            "copyright": name,
            "episode_id": video.id,
            "comment": "by Mefodii"
        }

        if File.exists(file_abs_path):
            Ffmpeg.add_tags(file_abs_path, tags)
        else:
            print("Not found: " + file_abs_path)


def datetime_tests():
    tt = "2020-04-08T20:20:20Z"
    if "." not in tt:
        tt = tt[:-1] + ".0Z"
    print(yt_to_py(tt))


def get_file_size():
    # Compare size of two files

    size = os.path.getsize("E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\mp3\\2022 Rewind - Animated 3D Porn Hentai Compilation, Part 11 Of 12 - 30+ Hourss.mkv")
    size2 = os.path.getsize("E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\mp3\\2022 Rewind - Animated 3D Porn Hentai Compilation, Part 12 Of 12 - 30+ Hourss.mkv")
    print(size)
    print(size2)
    print(size < size2)


def get_yt_id_from_video():
    video_id = "fpk6itC2Pq0"

    dk_file = paths.API_KEY_PATH
    worker = YoutubeWorker(dk_file)
    worker.get_channel_id_from_video(video_id)

    ic(worker.get_playlist_items("UUSHsSsgPaZ2GSmO6il8Cb5iGA", ""))


def test_if_yt_short():
    video_id = "Tyzk9JzQXgQ"

    dk_file = paths.API_KEY_PATH
    worker = YoutubeWorker(dk_file)
    worker.get_channel_id_from_video(video_id)


def check_yt_videos_order():
    pass


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    pass
    # -------===========------
    # db_file = '\\'.join([paths.DB_LOG_PATH, "ThePrimeCronus.txt"])
    # db_json = File.get_json_data(db_file)
    # -------===========------
    # test_http_ident(get_input_data())
    # -------===========------
    # yt_input = '/'.join([paths.INPUT_FILES_PATH, paths.YOUTUBE_JSON_FILE])
    # to_download = File.get_json_data(yt_input)
    # test_download_videos(to_download)
    # -------===========------
    # test_compose_unicode(get_input_data())
    # -------===========------
    # test_tags()
    # -------===========------
    get_yt_id_from_video()



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
