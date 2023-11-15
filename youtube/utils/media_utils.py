import os

from icecream import ic

from utils import file
from utils.file import File
from youtube.model.file_extension import FileExtension
from youtube.model.file_tags import FileTags
from youtube.utils.ffmpeg import Ffmpeg
from youtube.watchers.youtube.media import YoutubeVideo


def sync_media_filenames_with_db(db_file: str, media_paths: list[str], extension: FileExtension):
    """
    For each media file in list of paths, extract video ID of the file from file's metadata.

    If file's number is different from video's number in db, then filename and metadata will be updated.
    :param db_file:
    :param media_paths:
    :param extension:
    :return:
    """
    db_data = file.read_json(db_file)

    files = [f for path in media_paths for f in file.list_files(path)]
    media_files = filter_media_files(files, extension)

    for element in media_files:
        file_abs_path = element.get_abs_path()
        tags = Ffmpeg.read_metadata_json(file_abs_path, loglevel="error")
        file_id = tags.get(FileTags.DISC)
        if file_id is None:
            raise ValueError(f"File has no ID: {file_abs_path}")
        if db_data.get(file_id) is None:
            raise ValueError(f"File not found in DB: {file_abs_path}")

        video = YoutubeVideo.from_dict(db_data.get(file_id))
        media_number = int(tags.get(FileTags.TRACK))
        if media_number != video.number:
            tags = {
                FileTags.TRACK: str(video.number)
            }
            Ffmpeg.add_tags(file_abs_path, tags, loglevel="error")

            new_name = f"{video.file_name}.{extension.value}"
            new_abs_path = f"{element.path}\\{new_name}"
            print(f"Renaming: {element.get_plain_name()}. New name: {video.file_name}")
            os.rename(file_abs_path, new_abs_path)
        elif video.file_name != element.get_plain_name():
            print(f"Warning! Metadata equals but filenames not. DB: {video.file_name}. Media: {element.name}")


def validate_files_integrity(db_file: str, media_paths: list[str]):
    """
    Check that all items in db have the same number in playlist file.

    Check that all items in db with status "DOWNLOADED" have a file
    :param db_file:
    :param media_paths:
    :return:
    """
    db_data = file.read_json(db_file)

    for video_dict in db_data.values():
        video: YoutubeVideo = YoutubeVideo.from_dict(video_dict)
        if video.status != YoutubeVideo.STATUS_DOWNLOADED:
            continue

        found = False
        for madia_path in media_paths:
            abs_file_name = f"{madia_path}\\{video.file_name}.{video.file_extension.value}"
            if file.exists(abs_file_name):
                found = True
                break

        if not found:
            print(f"File not found: {video.file_name}. Video ID: {video.video_id}")


def filter_media_files(files: list[File], extension: FileExtension) -> list[File]:
    return list(filter(lambda f: f.extension == extension.value, files))
