from __future__ import unicode_literals
import time
from youtube import paths
from youtube.managers.yt_managers import MonitorManager, YoutubeQueueManager
from youtube.yt_api.requests import YoutubeWorker


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    monitors_db = paths.MAIN_MONITORS_PATH
    # monitors_db = paths.SIDE_MONITORS_PATH
    # monitors_db = paths.PGM_MONITORS_PATH
    monitors_db = paths.SECONDARY_MONITORS_PATH
    dk_file = paths.API_KEY_PATH

    worker = YoutubeWorker(dk_file)
    manager = MonitorManager(monitors_db, worker, paths.YOUTUBE_API_LOG)
    manager.check_for_updates()

    queue_manager = YoutubeQueueManager(paths.YOUTUBE_API_LOG)
    queue_manager.process_monitor_manager(manager)

    manager.append_tags()
    manager.update_track_list_log()
    manager.update_db_log()

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
