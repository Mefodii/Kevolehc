import os


PROJECT_PATH = "\\".join(os.getcwd().split("\\")[0:-1])
RESOURCES_PATH = PROJECT_PATH + "\\resources"
FILES_PATH = PROJECT_PATH + "\\files"
INPUT_FILES_PATH = FILES_PATH + "\\input"
LOGS_FILES_PATH = FILES_PATH + "\\logs"
MONITORS_FILES_PATH = FILES_PATH + "\\monitors"
YOUTUBE_RESULT_PATH = FILES_PATH + "\\mp3"
DB_LOG_PATH = FILES_PATH + "\\_db"

YOUTUBE_INPUT_FILE = "to_download.txt"
YOUTUBE_JSON_FILE = "yt_download.json"
YOUTUBE_MONITOR_FILE = "monitors.json"
YOUTUBE_MONITOR_FILE2 = "monitors2.json"
YOUTUBE_DK_FILE = "dk.txt"
YOUTUBE_DK_FILE2 = "dk_reserve.txt"

# LOGS
YOUTUBE_API_LOG = LOGS_FILES_PATH + "/api_logs.txt"
