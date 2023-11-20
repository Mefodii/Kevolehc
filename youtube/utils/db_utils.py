from utils import file
from youtube.utils import yt_datetime
from youtube.watchers.youtube.media import YoutubeVideo
from youtube.watchers.youtube.watcher import YoutubeWatcher


def add_videos(watcher: YoutubeWatcher) -> None:
    """
    Transform all watcher's videos to dict and append to watcher's db file.
    :param watcher:
    :return:
    """
    db_file = watcher.db_file
    db_videos = YoutubeVideo.from_db_file(db_file) if file.exists(db_file) else {}

    for video in watcher.videos:
        video_abs_path = video.get_file_abs_path()
        video.status = YoutubeVideo.STATUS_UNABLE
        if file.exists(video_abs_path):
            video.status = YoutubeVideo.STATUS_DOWNLOADED

        if v := db_videos.get(video.video_id):
            print(f"Warning!! Video with this ID already exists. Id: {v.video_id}. Number: {v.number}")
            print(f"Old publish date: {v.published_at}. New publish date: {video.published_at}")

        db_videos[video.video_id] = video

    YoutubeVideo.write(db_file, db_videos)


def shift_number(db_file: str, number: int, step: int = 1):
    """
    All videos with number greater or equal of given number will have its number changed by step.

    Update video file_name with new number
    :param db_file:
    :param number:
    :param step: how many position to shift. Negative as well
    :return:
    """
    db_videos = YoutubeVideo.from_db_file(db_file)

    shift_items(db_videos, position_start=number, position_end=None, step=step)

    YoutubeVideo.write(db_file, db_videos)


def move_video_number(db_file: str, video_id: str, new_number: int):
    """
    Shift down by 1 all videos with number larger than video_id.number until reaching new_number.
    And set video_id.number to new_number

    If video_id.number = 0, then shift by 1 all videos with number >= new_number
    :param db_file:
    :param video_id:
    :param new_number:
    :return:
    """
    db_videos = YoutubeVideo.from_db_file(db_file)

    video: YoutubeVideo = db_videos[video_id]
    if video.number == 0:
        shift_items(db_videos, position_start=new_number, position_end=None, step=1)
    elif video.number == new_number:
        print(f"Video already has this number. Video ID: {video_id}. Number: {new_number}")
        return
    else:
        del db_videos[video_id]
        if video.number > new_number:
            shift_items(db_videos, position_start=new_number, position_end=video.number, step=1)
        else:
            shift_items(db_videos, position_start=video.number, position_end=new_number, step=-1)

    video.number = new_number
    video.file_name = video.generate_file_name()
    db_videos[video.video_id] = video

    YoutubeVideo.write(db_file, db_videos)


def insert_video(db_file: str, video: YoutubeVideo):
    """
    Insert video to the video.number position and shift all other videos down.
    :param db_file:
    :param video:
    :return:
    """
    db_videos = YoutubeVideo.from_db_file(db_file)

    if db_videos.get(video.video_id):
        raise Exception(f"Video with this ID already exists in DB. ID: {video.video_id}")

    shift_items(db_videos, position_start=video.number, position_end=None, step=1)
    db_videos[video.video_id] = video

    YoutubeVideo.write(db_file, db_videos)


def delete_video(db_file: str, video_id: str):
    """
    Find video with given id and delete it from db. All other videos number is shifted by -1.
    :param db_file:
    :param video_id:
    :return:
    """
    db_videos = YoutubeVideo.from_db_file(db_file)

    position = db_videos[video_id].number
    del db_videos[video_id]

    shift_items(db_videos, position_start=position, position_end=None, step=-1)

    YoutubeVideo.write(db_file, db_videos)


def shift_items(items: dict[str, YoutubeVideo], position_start: int, position_end: int = None, step: int = 1):
    """
    All items within range position_start <= item.number <= position_end will have its number changed by given step.

    Items are mutated with new position number and file_name
    :param items:
    :param position_start: video number start position; inclusive
    :param position_end: video number end position; inclusive
    :param step: how many position to shift. Negative as well
    :return:
    """
    for video in items.values():
        if video.number >= position_start and (position_end is None or (position_end and video.number <= position_end)):
            video.number += step
            if video.number <= 0:
                raise Exception(f"Number <= 0 not allowed. Video ID: {video.video_id}")
            video.file_name = video.generate_file_name()
            items[video.video_id] = video


def check_validity(db_file: str) -> bool:
    """
    Check that each number from db_file is repeated exactly once.

    Check that numbers are sorted by published_at
    :param db_file:
    :return:
    """
    db_data = file.read_json(db_file)

    numbers: dict[int, YoutubeVideo] = {}
    valid = True
    for video_dict in db_data:
        video: YoutubeVideo = YoutubeVideo.from_dict(video_dict)
        if found_item := numbers.get(video.number):
            valid = False
            print(f"An video with number <{video.number}> already exists. "
                  f"Ids: [{found_item.video_id}, {video.video_id}]")
        else:
            numbers[video.number] = video

    max_number = max(numbers.keys())
    if valid:
        if item := numbers.get(0):
            valid = False
            print(f"Warning: db has a video with number 0. Video: {item.video_id}")

        for i in range(1, max_number+1):
            if numbers.get(i) is None:
                valid = False
                print(f"DB File missing number: {i}")

    if valid:
        videos = [YoutubeVideo.from_dict(v) for v in db_data]
        for i in range(len(videos) - 1):
            this_video = videos[i]
            next_video = videos[i+1]
            if this_video.number > next_video.number:
                valid = False
                print(f"Videos not sorted by number. IDs: {this_video.video_id}, {next_video.video_id}")
            if not next_video.published_at:
                valid = False
                print(next_video)
            if yt_datetime.compare_yt_dates(this_video.published_at, next_video.published_at) == 1:
                valid = False
                print(f"Videos not sorted by published_at. IDs: {this_video.video_id}, {next_video.video_id}")

    return valid
