import re
from .constants import NON_PARSED_CHARS, RESTRICTED_CHARS, DEFAULT_REPLACE_CHAR, CHARS_VARIATIONS


def replace_unicode_chars(video_title):
    processed_title = video_title
    for chars in NON_PARSED_CHARS:
        processed_title = processed_title.replace(chars[0], chars[1])

    return processed_title


def replace_restricted_file_chars(video_title):
    return re.sub('[' + re.escape(''.join(RESTRICTED_CHARS)) + ']',
                  DEFAULT_REPLACE_CHAR, video_title)


def normalize_file_name(video_title):
    return replace_restricted_file_chars(video_title)


def replace_chars_variations(text: str):
    result = text
    for chars_variation in CHARS_VARIATIONS:
        before = chars_variation[0]
        after = chars_variation[1]
        result = re.sub('[' + re.escape(''.join(before)) + ']', after, result)
    return result
