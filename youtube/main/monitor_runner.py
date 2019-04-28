from __future__ import unicode_literals
import os
import time
from youtube import paths
from youtube.managers.yt_managers import MonitorManager
from youtube.yt_api.requests import YoutubeWorker


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    monitors_db = '/'.join([paths.INPUT_FILES_PATH, paths.YOUTUBE_MONITOR_FILE])
    dk_file = '/'.join([paths.INPUT_FILES_PATH, paths.YOUTUBE_DK_FILE])

    worker = YoutubeWorker(dk_file)
    manager = MonitorManager(monitors_db, worker, paths.YOUTUBE_API_LOG)
    manager.check_for_updates()

    manager.finish()


#######################################################################################################################
# Process
#######################################################################################################################
if __name__ == "__main__":
    # Start time of the program
    start = time.time()

    # Main functionality
    __main__()

    # End time of the program
    end = time.time()
    # Running time of the program
    print("Program ran for: ", end - start, "seconds.")