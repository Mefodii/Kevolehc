import os

YOUTUBE_INPUT_FILE = "to_download.txt"
YOUTUBE_JSON_FILE = "yt_download.json"
YOUTUBE_WATCHERS_FILE = "yt_watchers.json"
YOUTUBE_WATCHERS_PGM_FILE = "yt_watchers_pgm.json"

YOUTUBE_DK_FILE = "dk.txt"

PROJECT_PATH = "\\".join(os.getcwd().split("\\")[0:-1])
RESOURCES_PATH = PROJECT_PATH + "\\resources"
FILES_PATH = PROJECT_PATH + "\\files"
INPUT_FILES_PATH = FILES_PATH + "\\input"
LOGS_FILES_PATH = FILES_PATH + "\\logs"
WATCHERS_DOWNLOAD_PATH = FILES_PATH + "\\watchers"
YOUTUBE_RESULT_PATH = FILES_PATH + "\\mp3"
DB_PATH = FILES_PATH + "\\_db"

# FULL PATH
YOUTUBE_WATCHERS_PATH = '/'.join([INPUT_FILES_PATH, YOUTUBE_WATCHERS_FILE])
YOUTUBE_WATCHERS_PGM_PATH = '/'.join([INPUT_FILES_PATH, YOUTUBE_WATCHERS_PGM_FILE])
YOUTUBE_PLAYLIST_PATH = "E:\\Google Drive\\Mu\\plist\\"

API_KEY_PATH = '/'.join([INPUT_FILES_PATH, YOUTUBE_DK_FILE])

# LOGS
YOUTUBE_API_LOG = LOGS_FILES_PATH + "/api_logs.txt"


