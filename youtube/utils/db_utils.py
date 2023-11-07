from utils import file
from youtube.watchers.youtube.media import YoutubeVideo
from youtube.watchers.youtube.watcher import YoutubeWatcher


def add_videos(watcher: YoutubeWatcher) -> None:
    """
    Transform all watcher's videos to dict and append to watcher's db file.
    :param watcher:
    :return:
    """
    db_file = watcher.db_file
    db_data = {}
    if file.exists(db_file):
        db_data = file.read_json(db_file)

    for video in watcher.videos:
        file_abs_path = video.get_file_abs_path()
        video.status = YoutubeVideo.STATUS_UNABLE
        if file.exists(file_abs_path):
            video.status = YoutubeVideo.STATUS_DOWNLOADED

        db_data[video.video_id] = video.to_dict()

    file.write_json(db_file, db_data)


def shift_number(db_file: str, number: int, step: int = 1):
    """
    All videos with number greater or equal of given number will have its number changed by step.

    Update video file_name with new number
    :param db_file:
    :param number:
    :param step: how many position to shift. Negative as well
    :return:
    """
    db_data = file.read_json(db_file)

    shift_items(db_data, position_start=number, position_end=None, step=step)

    file.write_json(db_file, db_data)


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
    db_data = file.read_json(db_file)

    video = YoutubeVideo.from_dict(db_data[video_id])
    if video.number == 0:
        shift_items(db_data, position_start=new_number, position_end=None, step=1)
    else:
        del db_data[video_id]
        if video.number > new_number:
            shift_items(db_data, position_start=new_number, position_end=video.number, step=1)
        else:
            shift_items(db_data, position_start=video.number, position_end=new_number, step=-1)

    video.number = new_number
    video.init_file_name()
    db_data[video.video_id] = video.to_dict()

    file.write_json(db_file, db_data)


def delete_video(db_file: str, video_id: str):
    """
    Find video with given id and delete it from db. All other videos number is shifted by -1.
    :param db_file:
    :param video_id:
    :return:
    """
    db_data = file.read_json(db_file)

    position = YoutubeVideo.from_dict(db_data[video_id]).number
    del db_data[video_id]

    shift_items(db_data, position_start=position, position_end=None, step=-1)

    file.write_json(db_file, db_data)


def shift_items(items: dict, position_start: int, position_end: int = None, step: int = 1):
    """
    All items within range position_start <= item.number <= position_end will have its number changed by given step.

    Items are mutated with new position number and file_name
    :param items:
    :param position_start: video number start position; inclusive
    :param position_end: video number end position; inclusive
    :param step: how many position to shift. Negative as well
    :return:
    """
    for video_id, video_dict in items.items():
        video = YoutubeVideo.from_dict(video_dict)
        if video.number >= position_start and (position_end is None or (position_end and video.number <= position_end)):
            video.number += step
            if video.number <= 0:
                raise Exception(f"Number <= 0 not allowed. Video ID: {video.video_id}")
            video.init_file_name()
            items[video.video_id] = video.to_dict()
