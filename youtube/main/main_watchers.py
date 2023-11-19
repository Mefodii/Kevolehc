from __future__ import unicode_literals
import time
from youtube import paths
from youtube.watchers.youtube.manager import YoutubeWatchersManager
from youtube.watchers.youtube.api import YoutubeWorker


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    youtube_watchers = paths.YOUTUBE_WATCHERS_PATH
    # youtube_watchers = paths.YOUTUBE_WATCHERS2_PATH
    # youtube_watchers = paths.YOUTUBE_WATCHERS_PGM_PATH
    dk_file = paths.API_KEY_PATH

    worker = YoutubeWorker(dk_file)
    manager = YoutubeWatchersManager(worker, youtube_watchers, paths.YOUTUBE_API_LOG)
    manager.run_full()


#######################################################################################################################
# Process
#######################################################################################################################
if __name__ == "__main__":
    # TODO - update dependencies (after all others todo's are done)
    # TODO - fix dynamic calls
    # TODO - remove unused imports
    # TODO - comment methods
    # Start time of the program
    start = time.time()

    # Main functionality
    __main__()

    # End time of the program
    end = time.time()
    # Running time of the program
    print("Program ran for: ", end - start, "seconds.")
