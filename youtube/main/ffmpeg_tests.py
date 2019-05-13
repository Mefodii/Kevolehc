from __future__ import unicode_literals
import os
import time
from youtube.managers.ffmpeg import Ffmpeg
from utils.File import get_file_name_with_extension
from youtube import paths
from youtube.managers.yt_managers import MonitorManager, YoutubeQueueManager
from youtube.yt_api.requests import YoutubeWorker


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    loc = "D:\\Automatica\\Python\\PyCharmProjects\\Kevolehc\\Kevolehc\\youtube\\files\\monitors\\Kurzgesagt"
    sample_image = loc + '\\sample.png'
    sample_mkv = loc + "\\sample.mkv"
    out_mkv = loc + "\\s2.mkv"

    # cmd2 = "ffmpeg -i " + sample_mkv + " -c copy -metadata title=\"Movie Title\" -metadata year=\"2010\" " \
    #                                    "-metadata dummy=\"by Mefodii\" " + out_mkv
    # cmd3 = "ffmpeg -i " + sample_mkv + " -c copy -attach " + sample_image + " -metadata:s:t mimetype=image/jpeg " + out_mkv
    # os.system(cmd2)

    # print(get_file_name_with_extension(loc, "4 - The Gulf Stream Explained"))

    Ffmpeg.merge_audio_and_video(loc, "audio.m4a", "video.mp4", "106 - Kurzgesagt – In a Nutshell - The Side Effects of Vaccines - How High is the Risk_.mkv")

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