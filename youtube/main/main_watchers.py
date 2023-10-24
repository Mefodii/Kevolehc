from __future__ import unicode_literals
import time
from youtube import paths
from youtube.watchers.youtube.manager import YoutubeWatchersManager
from youtube.watchers.youtube.api import YoutubeWorker


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    watchers_file = paths.YOUTUBE_WATCHERS_PATH
    # watchers_file = paths.YOUTUBE_WATCHERS2_PATH
    # watchers_file = paths.YOUTUBE_WATCHERS_PGM_PATH
    dk_file = paths.API_KEY_PATH

    worker = YoutubeWorker(dk_file)
    manager = YoutubeWatchersManager(watchers_file, worker, paths.YOUTUBE_API_LOG)
    manager.run_full()


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
