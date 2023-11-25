from youtube.watchers.youtube.media import YoutubeVideo, YoutubeVideoList


def shift(db_file: str, number: int, step: int = 1):
    """
    All videos with number greater or equal of given number will have its number changed by step.

    Update video file_name with new number
    :param db_file:
    :param number:
    :param step: how many position to shift. Negative as well
    :return:
    """
    video_list = YoutubeVideoList.from_file(db_file)
    video_list.shift_number(position_start=number, position_end=None, step=step)
    video_list.write(db_file, forced=True)


def move(db_file: str, video_id: str, new_number: int):
    """
    Find and delete video with current number. Then insert it with new_number
    :param db_file:
    :param video_id:
    :param new_number:
    :return:
    """
    video_list = YoutubeVideoList.from_file(db_file)

    video = video_list.get_by_id(video_id)
    if video is None:
        raise Exception(f"Item not found in playlist. ID: {video_id}")
    video_list.move(video, new_number)

    video_list.write(db_file, forced=True)


def insert(db_file: str, videos: list[YoutubeVideo]):
    """
    Insert video to the video number position and shift all other videos down.
    :param db_file:
    :param videos:
    :return:
    """
    video_list = YoutubeVideoList.from_file(db_file)

    for video in videos:
        video_list.insert(video)

    video_list.write(db_file, forced=True)


def delete(db_file: str, videos_id: list[str]):
    """
    Find video with given id and delete it from db. All other videos number is shifted by -1.
    :param db_file:
    :param videos_id:
    :return:
    """
    video_list = YoutubeVideoList.from_file(db_file)
    for video_id in videos_id:
        video = video_list.get_by_id(video_id)
        if video is None:
            raise Exception(f"Video not found in DB. ID: {video_id}")

        video_list.delete(video)
    video_list.write(db_file)
