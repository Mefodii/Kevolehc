import os

from icecream import ic

from utils import file
from utils.file import File
from youtube import paths
from youtube.model.file_extension import FileExtension
from youtube.model.file_tags import FileTags
from youtube.utils.ffmpeg import Ffmpeg
from youtube.watchers.youtube.media import YoutubeVideo


def sync_media_filenames_with_db(db_file: str, media_path: str, extension: FileExtension):
    db_data = file.read_json(db_file)
    media_files = filter_media_files(file.list_files(media_path), extension)

    for element in media_files:
        file_abs_path = element.get_abs_path()
        tags = Ffmpeg.read_metadata_json(file_abs_path)
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
            Ffmpeg.add_tags(file_abs_path, tags)

            new_file_name = element.path + "\\" + video.file_name + "." + extension.value
            os.rename(file_abs_path, new_file_name)


def filter_media_files(files: list[File], extension: FileExtension) -> list[File]:
    return list(filter(lambda f: f.extension == extension.value, files))
