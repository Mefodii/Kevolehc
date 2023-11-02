from __future__ import unicode_literals
import time

from icecream import ic

from utils import File
from youtube.model.file_extension import FileExtension
from youtube.model.playlist_item import PlaylistItem
from youtube.utils.ffmpeg import Ffmpeg
from youtube import paths
from youtube.watchers.youtube.media import YoutubeVideo
from youtube.watchers.youtube.api import YoutubeWorker
from youtube.utils.yt_datetime import yt_to_py, compare_yt_dates

from youtube.watchers.youtube.watcher import YoutubeWatcher


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


def test_playlist_item_class():
    dk_file = paths.API_KEY_PATH
    worker = YoutubeWorker(dk_file)
    dummy_watcher = YoutubeWatcher.dummy()
    dummy_watcher.video_count = 3230
    items = worker.get_channel_uploads_from_date("UCm3-xqAh3Z-CwBniG1u_1vw", "2023-10-14T06:20:50.193Z")
    for item in items:
        dummy_watcher.video_count += 1
        yt_video = YoutubeVideo.from_youtube_api_video_and_watcher(item, dummy_watcher)
        dummy_watcher.append_video(yt_video)

    output = []
    for video in dummy_watcher.videos:
        item = PlaylistItem.from_youtubevideo(video)
        output.append(str(item))

    File.write("E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\tests\\res.txt", output)


def test_playlist_from_str():
    data = File.read("E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\tests\\res.txt",
                     File.ENCODING_UTF8)
    items = []
    item = None
    for line in data:
        if PlaylistItem.is_playlist_str(line):
            item = PlaylistItem.from_str(line)
            items.append(item)
        else:
            item.append_child(line)

    res = []
    for item in items:
        res.append(str(item))
        [res.append(child) for child in item.children]
    File.write("E:\\Coding\\Projects\\Kevolehc\\Kevolehc\\youtube\\files\\tests\\res2.txt", res,
               File.ENCODING_UTF8)


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    pass
    test_playlist_from_str()


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
