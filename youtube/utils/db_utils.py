from utils import file
from youtube.utils import yt_datetime
from youtube.watchers.youtube.media import YoutubeVideo


def append(db_file: str, videos: list[YoutubeVideo], create_file_if_not_found: bool = False):
    if not create_file_if_not_found and not file.exists(db_file):
        raise Exception(f"DB file not found: {db_file}")

    db_videos = YoutubeVideo.from_db_file(db_file) if file.exists(db_file) else {}

    for video in videos:
        if v := db_videos.get(video.video_id):
            print(f"Warning!! Video with this ID already exists. Id: {v.video_id}. Number: {v.number}")
            print(f"Overwritting!! Old video: {v}. New video: {video}")

        db_videos[video.video_id] = video

    YoutubeVideo.write(db_file, db_videos)


def shift(db_file: str, number: int, step: int = 1):
    """
    All videos with number greater or equal of given number will have its number changed by step.

    Update video file_name with new number
    :param db_file:
    :param number:
    :param step: how many position to shift. Negative as well
    :return:
    """
    db_videos = YoutubeVideo.from_db_file(db_file)

    shift_videos(db_videos, position_start=number, position_end=None, step=step)

    YoutubeVideo.write(db_file, db_videos)


def move(db_file: str, video_id: str, new_number: int):
    """
    Find and delete video with current number. Then insert it with new_number
    :param db_file:
    :param video_id:
    :param new_number:
    :return:
    """
    db_videos = YoutubeVideo.from_db_file(db_file)

    video = delete_video(db_videos, video_id)
    if video.number == new_number:
        print(f"Video already has this number. Move canceleld. Video id: {video.video_id}. Number: {new_number}")
        return

    video.number = new_number
    video.file_name = video.generate_file_name()
    insert_video(db_videos, video)

    YoutubeVideo.write(db_file, db_videos)


def insert(db_file: str, videos: list[YoutubeVideo]):
    """
    Insert video to the video number position and shift all other videos down.
    :param db_file:
    :param videos:
    :return:
    """
    db_videos = YoutubeVideo.from_db_file(db_file)

    for video in videos:
        insert_video(db_videos, video)

    YoutubeVideo.write(db_file, db_videos)


def delete(db_file: str, videos_id: list[str]):
    """
    Find video with given id and delete it from db. All other videos number is shifted by -1.
    :param db_file:
    :param videos_id:
    :return:
    """
    db_videos = YoutubeVideo.from_db_file(db_file)
    for video_id in videos_id:
        delete_video(db_videos, video_id)
    YoutubeVideo.write(db_file, db_videos)


def shift_videos(videos: dict[str, YoutubeVideo], position_start: int, position_end: int = None, step: int = 1):
    """
    All items within range position_start <= item.number <= position_end will have its number changed by given step.

    Items are mutated with new position number and file_name
    :param videos:
    :param position_start: video number start position; inclusive
    :param position_end: video number end position; inclusive
    :param step: how many position to shift. Negative as well
    :return:
    """
    for video in videos.values():
        if video.number >= position_start and (position_end is None or (position_end and video.number <= position_end)):
            video.number += step
            if video.number <= 0:
                raise Exception(f"Number <= 0 not allowed. Video ID: {video.video_id}")
            video.file_name = video.generate_file_name()
            videos[video.video_id] = video


def delete_video(videos: dict[str, YoutubeVideo], video_id: str) -> YoutubeVideo:
    """
    Find and remove video with given id.

    All items after removed item are shifted down by 1.
    :param videos:
    :param video_id:
    :return:
    """
    video = videos.get(video_id)
    if video is None:
        raise Exception(f"Video not found in DB. ID: {video_id}")

    del videos[video_id]
    shift_videos(videos, position_start=video.number, position_end=None, step=-1)
    return video


def insert_video(videos: dict[str, YoutubeVideo], video: YoutubeVideo):
    """
    Shift up by 1 all videos, then insert given item
    :param videos:
    :param video:
    :return:
    """
    if videos.get(video.video_id):
        raise Exception(f"Video already exists in DB. ID: {video.video_id}")
    if video.number == -1:
        video.number = calculate_insert_number(videos, video.published_at)
        video.file_name = video.generate_file_name()

    shift_videos(videos, position_start=video.number, position_end=None, step=1)
    videos[video.video_id] = video


def calculate_insert_number(videos: dict[str, YoutubeVideo], published_at: str) -> int:
    """
    Calculate video number based on published_at value
    :param videos:
    :param published_at:
    :return:
    """
    videos_list: list[YoutubeVideo] = list(sorted(videos.values(), key=lambda v: v.number))
    for video in videos_list:
        if yt_datetime.compare_yt_dates(video.published_at, published_at) == 1:
            return video.number

    return videos_list[-1].number + 1


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

        for i in range(1, max_number + 1):
            if numbers.get(i) is None:
                valid = False
                print(f"DB File missing number: {i}")

    if valid:
        videos = [YoutubeVideo.from_dict(v) for v in db_data]
        for i in range(len(videos) - 1):
            this_video = videos[i]
            next_video = videos[i + 1]
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
