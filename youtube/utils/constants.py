RESTRICTED_CHARS = ['<', '>', ':', '\"', '/', '\\', '?', '*', '|']
DEFAULT_REPLACE_CHAR = "_"
NON_PARSED_CHARS = [
    ["&#39;", "'"],
    ["&quot;", "'"],
    ["&amp;", "&"]
]

CHARS_VARIATIONS = (
    (("—", "‒", "–"), "-"),
    (("’", "`"), "'")
)

DEFAULT_YOUTUBE_WATCH = "https://www.youtube.com/watch?v="
ALLOWED_VIDEO_QUALITY = [720, 1080]
