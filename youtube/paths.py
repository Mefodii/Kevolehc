import os


PROJECT_PATH = "\\".join(os.getcwd().split("\\")[0:-1])
RESOURCES_PATH = PROJECT_PATH + "/resources"
FILES_PATH = PROJECT_PATH + "/files"
INPUT_FILES_PATH = FILES_PATH + "/input"
YOUTUBE_RESULT_PATH = FILES_PATH + "/mp3"

YOUTUBE_INPUT_FILE = "to_download.txt"
YOUTUBE_MONITOR_FILE = "youtube_monitors.txt"
YOUTUBE_DK_FILE = "dk.txt"
