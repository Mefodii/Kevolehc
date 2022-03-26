from __future__ import unicode_literals
import os
import time
import sys
import traceback

from youtube.model.downloader import YoutubeDownloader
from youtube.model.yt_queue import YoutubeQueue

from youtube import paths
from youtube.settings.settings import YTDownloadSettings
from youtube.utils import constants
from utils import File

DEFAULT_SETTINGS = "settings.json"
FORMATTED_OUTPUT = "<!>"
SEPARATOR = ";"

DEFAULT_TITLE = '%(title)s'
DEFAULT_EXTENSION = constants.MP3


def process_my_location():
    abs_path = repr(sys.argv[0])[1:-1]

    split_by = "/"
    if "\\" in abs_path:
        split_by = "\\"

    return "\\".join(abs_path.split(split_by)[0:-1])


MY_LOCATION = process_my_location()


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def print_traceback():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
    traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)
    traceback.print_exc()
    formatted_lines = traceback.format_exc().splitlines()
    print(formatted_lines[0])
    print(formatted_lines[-1])
    print(repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))
    print(repr(traceback.extract_tb(exc_traceback)))
    print(repr(traceback.format_tb(exc_traceback)))


def parse_input_line(line):
    title = DEFAULT_TITLE
    extension = DEFAULT_EXTENSION
    url = line

    if line.startswith(FORMATTED_OUTPUT):
        _, title, extension, url = line.split(SEPARATOR)
        if len(title) == 0:
            title = DEFAULT_TITLE
        if len(extension) == 0:
            extension = DEFAULT_EXTENSION

    if len(url) == 0:
        raise Exception("Url should not be empty")

    return title, extension, url


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__(settings_file):
    os.chdir(MY_LOCATION)
    print("Started at: " + MY_LOCATION)
    if settings_file:
        settings = YTDownloadSettings(settings_file)

        input_file = '/'.join([MY_LOCATION, settings.input_file])
        output_directory = '/'.join([MY_LOCATION, settings.output_directory])
        resources_path = '/'.join([MY_LOCATION, settings.resources_path])
    else:
        input_file = '/'.join([paths.INPUT_FILES_PATH, paths.YOUTUBE_INPUT_FILE])
        output_directory = paths.YOUTUBE_RESULT_PATH
        resources_path = paths.RESOURCES_PATH

    downloader = YoutubeDownloader(resources_path)

    input_lines = File.get_file_lines(input_file, "8")
    i = 1
    total_to_download = len(input_lines)
    for input_line in input_lines:
        print("".join(["Downloading ", str(i), "/", str(total_to_download)]))

        title, extension, url = parse_input_line(input_line)
        queue = YoutubeQueue("", title, output_directory, extension, link=url)
        downloader.download(queue)

        i += 1


#######################################################################################################################
# Process
#######################################################################################################################
if __name__ == "__main__":
    # Start time of the program
    start = time.time()

    # Main functionality
    try:
        args = sys.argv

        if len(args) > 1:
            if args[1] == "local":
                __main__(None)
            else:
                print("Argument not valid")
        else:
            __main__(DEFAULT_SETTINGS)
    except:
        print_traceback()
        input("Press enter to end")
        raise

    # End time of the program
    end = time.time()
    # Running time of the program
    print("Program ran for: ", end - start, "seconds.")