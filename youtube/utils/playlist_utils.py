from youtube.model.playlist_item import PlaylistItem
from youtube.utils import constants
from youtube.watchers.youtube.media import YoutubeVideo


def shift(playlist_file: str, number: int, step: int = 1):
    """
    All videos with number greater or equal of given number will have its number changed by step.

    Update video file_name with new number
    :param playlist_file:
    :param number:
    :param step: how many position to shift. Negative as well
    :return:
    """
    playlist_items = PlaylistItem.from_file(playlist_file)
    shift_items(playlist_items, position_start=number, position_end=None, step=step)
    PlaylistItem.write(playlist_file, playlist_items)


def move(playlist_file: str, video_url: str, new_number: int):
    """
    Find and delete item from current number. Then insert it with new_number

    Playlist file must be sorted
    :param playlist_file:
    :param video_url: full url, with http and stuff
    :param new_number:
    :return:
    """
    playlist_items = PlaylistItem.from_file(playlist_file)
    if not is_sorted(playlist_items):
        raise Exception(f"Cannot move video. Playlist is not properly sorted by track_nr. File: {playlist_file}")

    item = delete_item(playlist_items, video_url)
    if item.track_nr == new_number:
        print(f"Video already has this number. Move canceleld. Video url: {item.url}. Number: {new_number}")
        return

    item.track_nr = new_number
    insert_item(playlist_items, item)

    PlaylistItem.write(playlist_file, playlist_items)


def insert(playlist_file: str, items: list[PlaylistItem]):
    """
    Insert items to the item.track_nr position and shift all other items down
    :param playlist_file:
    :param items:
    :return:
    """
    playlist_items = PlaylistItem.from_file(playlist_file)

    for i in items:
        insert_item(playlist_items, i)

    PlaylistItem.write(playlist_file, playlist_items)


def delete(playlist_file: str, videos_url: list[str]):
    """
    Find video with given id and delete it from file. All other videos number is shifted by -1.
    :param playlist_file:
    :param videos_url: list with full url, with http and stuff
    :return:
    """
    playlist_items = PlaylistItem.from_file(playlist_file)

    for url in videos_url:
        delete_item(playlist_items, url)

    PlaylistItem.write(playlist_file, playlist_items)


def shift_items(items: list[PlaylistItem], position_start: int, position_end: int = None, step: int = 1):
    """
    All items within range position_start <= item.track_nr <= position_end will have its number changed by given step.

    Items are mutated with new position number
    :param items:
    :param position_start: video number start position; inclusive
    :param position_end: video number end position; inclusive
    :param step: how many position to shift. Negative as well
    :return:
    """
    for playlist_item in items:
        if playlist_item.is_dummy:
            continue

        if (playlist_item.track_nr >= position_start and
                (position_end is None or (position_end and playlist_item.track_nr <= position_end))):
            playlist_item.track_nr += step
            if playlist_item.track_nr <= 0:
                raise Exception(f"Number <= 0 not allowed. Video ID: {playlist_item.url}")


def add_missing_track_number(playlist_file: str, db_file: str):
    """
    If a playlist item has no number, find it in db_file and update playlist item.
    :param playlist_file:
    :param db_file:
    :return:
    """
    db_videos = YoutubeVideo.from_db_file(db_file)
    playlist_items = PlaylistItem.from_file(playlist_file)

    changed = False
    for item in playlist_items:
        if item.is_dummy:
            continue

        if item.track_nr is None:
            video_id = item.url.replace(constants.DEFAULT_YOUTUBE_WATCH, "")
            db_video = db_videos[video_id]
            if db_video is None:
                raise Exception(f"Video not found in DB. Video ID: {video_id}")

            item.track_nr = db_video.number
            changed = True

    if changed:
        PlaylistItem.write(playlist_file, playlist_items)


def delete_item(items: list[PlaylistItem], item_url: str) -> PlaylistItem:
    """
    Find and remove item with given url.

    All items after removed item are shifted down by 1.
    :param items:
    :param item_url:
    :return:
    """
    item = find_item(items, item_url)
    if item is None:
        raise Exception(f"Item not found in playlist. ID: {item_url}")

    items.remove(item)
    shift_items(items, position_start=item.track_nr, position_end=None, step=-1)

    return item


def insert_item(items: list[PlaylistItem], item: PlaylistItem):
    """
    Shift up by 1 all items, then insert given item
    :param items:
    :param item:
    :return:
    """
    if find_item(items, item.url):
        raise Exception(f"Item already exists in playlist. ID: {item.url}")

    shift_items(items, position_start=item.track_nr, position_end=None, step=1)

    inserted = False
    for i in range(len(items)):
        if items[i].is_dummy:
            continue

        if items[i].track_nr > item.track_nr:
            items.insert(i, item)
            inserted = True
            break

    if not inserted:
        items.append(item)


def find_item(items: list[PlaylistItem], url: str) -> PlaylistItem | None:
    """
    :param items:
    :param url:
    :return: First PlaylistItem with given url. None if not found.
    """
    for i in range(len(items)):
        if items[i].url == url:
            return items[i]

    return None


def is_sorted(items: list[PlaylistItem]) -> bool:
    """
    :param items:
    :return: True if all items in list are sorted ascending by track_nr, no duplicates
    """
    expected_nr = 1
    for item in items:
        if item.is_dummy:
            continue

        if item.track_nr != expected_nr:
            print(f"Item has unsorted track nr: {item.track_nr}. Item: {item}. Expected track nr: {expected_nr}")
            return False
        expected_nr += 1

    return True


def check_validity(playlist_file: str, db_file: str) -> bool:
    """
    Check that playlist is sorted.

    Check that all videos from db are in playlist and no extras.
    :param playlist_file:
    :param db_file:
    :return:
    """
    db_videos = YoutubeVideo.from_db_file(db_file)
    playlist_items = PlaylistItem.from_file(playlist_file)

    if not is_sorted(playlist_items):
        return False

    items_dict: dict[str, PlaylistItem] = {item.url.replace(constants.DEFAULT_YOUTUBE_WATCH, ""): item
                                           for item in playlist_items}
    valid = True
    for db_video in db_videos.values():
        item = items_dict.pop(db_video.video_id, None)
        if not item:
            valid = False
            print(f"Video not found in playlist. Video: {db_video}")

        if item.track_nr != db_video.number:
            valid = False
            print(f"Mismatch number. ID: {db_video.video_id}. DB_NR: {db_video.number}. PL_NR: {item.track_nr}")

    for item in items_dict.values():
        if not item.is_dummy:
            valid = False
            print(f"Extra item in playlist. Item: {item}")

    return valid

