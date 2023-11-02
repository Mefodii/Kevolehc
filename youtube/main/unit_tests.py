from __future__ import unicode_literals

import os
import time

from icecream import ic

from utils import File
from youtube.paths import TESTS_PATH
from youtube.utils import playlist_utils, db_utils
from youtube.utils.yt_datetime import yt_to_py
from youtube.watchers.youtube.media import YoutubeVideo

TEST_READ_WRITE_PLAYLIST = "\\".join([TESTS_PATH, "test_read_write_playlist.txt"])
TEST_ADD_PLAYLIST_TRACKS = "\\".join([TESTS_PATH, "test_add_playlist_tracks.txt"])
TEST_ADD_PLAYLIST_TRACKS_DB = "\\".join([TESTS_PATH, "test_add_playlist_tracks_db.txt"])
TEST_ADD_PLAYLIST_TRACKS_RES = "\\".join([TESTS_PATH, "test_add_playlist_tracks_res.txt"])
TEST_PLAYLIST_SHIFT = "\\".join([TESTS_PATH, "test_playlist_shift.txt"])
TEST_PLAYLIST_DEL = "\\".join([TESTS_PATH, "test_playlist_del.txt"])
TEST_PLAYLIST_MOVE = "\\".join([TESTS_PATH, "test_playlist_move.txt"])

TEST_READ_WRITE_DB = "\\".join([TESTS_PATH, "test_read_write_db.txt"])
TEST_DB_SHIFT = "\\".join([TESTS_PATH, "test_db_shift.txt"])
TEST_DB_DEL = "\\".join([TESTS_PATH, "test_db_del.txt"])
TEST_DB_MOVE = "\\".join([TESTS_PATH, "test_db_move.txt"])


def files_content_equal(f1, f2) -> bool:
    """
    read and compare the content of 2 files
    :param f1:
    :param f2:
    :return:
    """
    f1_data = File.read(f1, encoding=File.ENCODING_UTF8)
    f2_data = File.read(f2, encoding=File.ENCODING_UTF8)

    if len(f1_data) != len(f2_data):
        ic(f"Files length not equal. F1: {f1}. F2: {f2}")
        return False

    for i in range(len(f1_data)):
        if f1_data[i] != f2_data[i]:
            ic(f"Lines not equal. Line: {i + 1}. F1: {f1}. F2: {f2}")
            return False

    return True


def test_yt_to_py():
    a = yt_to_py("2019-06-04T06:16:06.816Z")
    b = yt_to_py("2019-06-04T06:16:06.816Z")
    c = yt_to_py("2019-06-04T06:16:06.817Z")
    d = yt_to_py("2019-06-04T06:16:06.815Z")
    f = yt_to_py("2019-06-04T06:15:06.816Z")

    if not a == b:
        ic(f"Expected a == b. a: {a}. b: {b}")
    if not a < c:
        ic(f"Expected a < b. a: {a}. c: {b}")
    if not a > d:
        ic(f"Expected a > d. a: {a}. d: {b}")
    if not a > f:
        ic(f"Expected a > f. a: {a}. f: {f}")


def test_read_write_db_file():
    """
    Test that db utils is correctly read to object then converted back to json with no anomalies.
    :return:
    """
    db_data = File.read_json(TEST_READ_WRITE_DB)

    videos = [YoutubeVideo.from_dict(video_dict) for video_dict in db_data.values()]
    output_items = {video.video_id: video.to_dict() for video in videos}

    output_file = TESTS_PATH + "\\" + test_read_write_playlist_file.__name__ + "temp.txt"
    File.write_json(output_file, output_items)

    if files_content_equal(TEST_READ_WRITE_DB, output_file):
        os.remove(output_file)


def test_db_utils():
    db_data = File.read_json(TEST_READ_WRITE_DB)
    output_file = TESTS_PATH + "\\" + test_db_utils.__name__ + "temp.txt"

    File.write_json(output_file, db_data)
    db_utils.shift_number(output_file, 7, 3)
    if not files_content_equal(TEST_DB_SHIFT, output_file):
        return

    File.write_json(output_file, db_data)
    db_utils.move_video_number(output_file, "M-vGUWt9BLI", 3)
    if not files_content_equal(TEST_DB_MOVE, output_file):
        return

    File.write_json(output_file, db_data)
    db_utils.delete_video(output_file, "NvRHXnb039Q")
    if not files_content_equal(TEST_DB_DEL, output_file):
        return

    os.remove(output_file)


def test_read_write_playlist_file():
    """
    Test that playlist utils is correctly read to object then converted back to string with no anomalies.
    :return:
    """
    playlist_items = playlist_utils.read_playlist(TEST_READ_WRITE_PLAYLIST)
    output_file = TESTS_PATH + "\\" + test_read_write_playlist_file.__name__ + "temp.txt"
    playlist_utils.write_playlist(output_file, playlist_items)

    if files_content_equal(TEST_READ_WRITE_PLAYLIST, output_file):
        os.remove(output_file)


def test_playlist_utils():
    playlist_items = playlist_utils.read_playlist(TEST_READ_WRITE_PLAYLIST)
    output_file = TESTS_PATH + "\\" + test_playlist_utils.__name__ + "temp.txt"
    playlist_utils.write_playlist(output_file, playlist_items)

    playlist_utils.add_missing_track_number(output_file, TEST_ADD_PLAYLIST_TRACKS_DB)

    if not files_content_equal(TEST_ADD_PLAYLIST_TRACKS_RES, output_file):
        return

    playlist_items = playlist_utils.read_playlist(output_file)
    playlist_utils.shift_number(output_file, 500, 3)
    if not files_content_equal(TEST_PLAYLIST_SHIFT, output_file):
        return

    playlist_utils.write_playlist(output_file, playlist_items)
    playlist_utils.move_video_number(output_file, "https://www.youtube.com/watch?v=y0Lm-4O4Fr4", 500)
    if not files_content_equal(TEST_PLAYLIST_MOVE, output_file):
        return

    playlist_utils.write_playlist(output_file, playlist_items)
    playlist_utils.delete_video(output_file, "https://www.youtube.com/watch?v=y0Lm-4O4Fr4")
    if not files_content_equal(TEST_PLAYLIST_DEL, output_file):
        return

    os.remove(output_file)


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    test_yt_to_py()
    test_db_utils()
    test_read_write_db_file()
    test_read_write_playlist_file()
    test_playlist_utils()


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
