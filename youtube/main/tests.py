from __future__ import unicode_literals
import time

from icecream import ic

from utils import File
from youtube.model.file_extension import FileExtension
from youtube.utils.ffmpeg import Ffmpeg
from youtube import paths
from youtube.watchers.youtube.media import YoutubeVideo
from youtube.watchers.youtube.api import YoutubeWorker
from youtube.utils.yt_datetime import yt_to_py, compare_yt_dates
from unicodedata import normalize


def test_yt_to_py():
    a = yt_to_py("2019-06-04T06:16:06.816Z")
    b = yt_to_py("2019-06-04T06:16:06.816Z")
    c = yt_to_py("2019-06-04T06:16:06.817Z")
    d = yt_to_py("2019-06-04T06:16:06.815Z")
    f = yt_to_py("2019-06-04T06:15:06.816Z")

    print(a == b)
    print(a == c)
    print(a == d)
    print(a < b)
    print(a > f)


def test_compose_unicode(data):
    result = []

    composed = False
    for line in data:
        normalized = normalize('NFC', line)
        result.append(normalized[:-1])
        if not normalized == line:
            composed = True

    print(composed)
    File.write("C:\\Users\\Mefodii\\Downloads\\nfc.txt", result, File.ENCODING_UTF8)


# Create the DB file from already downloaded files
def add_to_db():
    name = "ThePrimeThanatos"
    check_path = "G:\\Music\\" + name
    extension = FileExtension.MP3
    result_path = "E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\_db"
    db_file = result_path + "\\" + name + ".txt"
    files_list = File.list_files(check_path)

    result = {}
    for element in files_list:
        abs_path = element["path"] + "\\" + element["filename"]
        if extension.is_video():
            if abs_path.endswith(extension.value):
                metadata = Ffmpeg.metadata_to_json(Ffmpeg.get_metadata(abs_path))
                episode_id = metadata.get("EPISODE_ID", None)
                if episode_id:
                    title = metadata.get("TITLE")
                    track = metadata.get("TRACK")
                    result[episode_id] = {"TITLE": title, "STATUS": "DOWNLOADED", "NUMBER": track, "CHANNEL_NAME": name,
                                          "FILE_NAME": element["filename"], "FORMAT": extension.value}

        if extension.is_audio():
            if abs_path.endswith(extension):
                metadata = Ffmpeg.metadata_to_json(Ffmpeg.get_metadata(abs_path))
                episode_id = metadata.get("DISC", None)
                if episode_id:
                    title = metadata.get("TITLE")
                    track = metadata.get("TRACK")
                    result[episode_id] = {"TITLE": title, "STATUS": "DOWNLOADED", "NUMBER": track, "CHANNEL_NAME": name,
                                          "FILE_NAME": element["filename"], "FORMAT": extension.value}

    File.write_json(db_file, result)


#  Add to position 168 track number if it does not exist
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


def datetime_tests():
    tt = "2020-04-08T20:20:20Z"
    if "." not in tt:
        tt = tt[:-1] + ".0Z"
    print(yt_to_py(tt))


def test_video_sort_order():
    dk_file = paths.API_KEY_PATH
    worker = YoutubeWorker(dk_file)
    items = worker.get_channel_uploads_from_date("UCaNd66xUJjX8VZT6AByVpiw", "2010-10-10T06:20:16.813Z")
    for i in range(0, len(items) - 1):
        date_compare = compare_yt_dates(items[i].get_publish_date(), items[i+1].get_publish_date())

        if date_compare == -1:
            ic(items[i], items[i+1])

    for item in items:
        publish_fields_equals = item.get_publish_date() == item.data.get("snippet").get("publishedAt")
        if not publish_fields_equals:
            ic(item.data)


def test_video_duration():
    dk_file = paths.API_KEY_PATH
    worker = YoutubeWorker(dk_file)
    items = worker.get_channel_uploads_from_date("UCmYTgpKxd-QOJCPDrmaXuqQ", "2023-10-14T06:20:50.193Z")
    ids = ([item.get_id() for item in items] +
           ["9t4P_i0OvZk", "q6dbhgandUw", "pKij-ygut5E", "AgpWX18dby4", "9HNJkfoXb8o"])
    videos = worker.get_videos(ids)
    for video in videos:
        if not video.has_valid_duration():
            ic(video.get_title())


def add_tags_to_db():
    files = File.list_files(paths.DB_PATH)
    for file in files:
        db_file = f"{file[File.PATH]}\\{file[File.FILENAME]}"
        ic(db_file)

        data = File.read_json(db_file)

        for video_dict in data.values():
            video = YoutubeVideo.from_dict(video_dict)
            data[video.video_id] = video.to_dict()

        File.write_json(db_file, data)


def test():
    db_file = f"{paths.DB_PATH}\\Bob42jh.txt"
    data = File.read_json(db_file)
    test_data = {}
    for video_dict in data.values():
        video = YoutubeVideo.from_dict(video_dict)
        test_data[video.video_id] = video.to_dict()

    File.write_json(db_file, test_data)


def test_scaling():
    bitrate_name = "E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\tests\\bitrate.mkv"
    resize_name = "E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\tests\\resize.mkv"
    randbit_name = "E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\tests\\randbit2.mkv"
    bandre_name = "E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\tests\\bandre.mkv"
    Ffmpeg.resize(randbit_name, height=720, scale_bitrate=True)


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
    test_scaling()


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
