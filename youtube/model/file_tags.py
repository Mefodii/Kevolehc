from youtube.model.file_extension import FileExtension
from youtube.watchers.youtube.media import YoutubeVideo


class FileTags:
    AUTHOR = "author"
    COPYRIGHT = "copyright"
    COMMENT = "comment"
    DISC = "disc"
    EPISODE_ID = "episode_id"
    GENRE = "genre"
    TITLE = "title"
    TRACK = "track"

    @staticmethod
    def extract_from_youtubevideo(item: YoutubeVideo) -> dict:
        tags = {
            FileTags.TITLE: item.title,
            FileTags.TRACK: str(item.number),
            FileTags.COPYRIGHT: item.channel_name,
            FileTags.COMMENT: "by Mefodii"
        }
        if item.file_extension == FileExtension.MP3:
            tags[FileTags.GENRE] = item.channel_name
            tags[FileTags.DISC] = item.video_id
        else:
            tags[FileTags.AUTHOR] = item.channel_name
            tags[FileTags.EPISODE_ID] = item.video_id

        return tags
