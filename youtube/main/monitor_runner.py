from __future__ import unicode_literals
import os
import time
from youtube import paths
from youtube.model.yt_monitors import MonitorManager


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    monitors_db = '/'.join([paths.INPUT_FILES_PATH, paths.YOUTUBE_MONITOR_FILE])
    manager = MonitorManager(monitors_db)
    print(repr(manager))

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