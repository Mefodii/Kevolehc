from os import listdir
from os.path import isfile, join, isdir
import time
from utils import File
import ast

from mutagen.easyid3 import EasyID3

from metaread.constants import constants, paths


def list_files(path):
    return [{'path': path, 'filename': f} for f in listdir(path) if isfile(join(path, f))]


def list_dirs(path):
    return [join(path, f) for f in listdir(path) if isdir(join(path, f))]


def get_data(path, recursive=None):
    data = []
    if recursive is None:
        recursive = True

    data += list_files(path)

    if not recursive:
        return data

    for directory in list_dirs(path):
        data += get_data(directory)

    return data


def filter_audio_files(data):
    result = []
    for element in data:
        if is_audio_file(element["filename"]):
            result.append(element)

    return result


def is_audio_file(filename):
    file_extension = filename.split(".")[-1]
    if any(file_extension in s for s in constants.VALID_AUDIO_FORMATS):
        return True
    return False


def enrich_metadata(data):
    result = []
    for element in data:
        full_path = join(element["path"], element["filename"])
        element = {**element, **ast.literal_eval(str(EasyID3(full_path)))}
        result.append(element)

    return result


def print_titles(output_filename, data):
    path = join(paths.TITLES_OUTPUT_PATH, output_filename)
    lines = []
    for element in data:
        lines.append(element["title"][0])

    lines = sorted(set(lines), key=lambda s: s.lower())
    File.write_lines_to_file_utf8(path, lines)


def list_titles(artist, path):
    files = get_data(path, recursive=True)
    audio_files = filter_audio_files(files)
    audio_files = enrich_metadata(audio_files)
    print_titles(artist, audio_files)


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    artist = "The Star Killers"
    current_directory = "D:/My Music/To Be Listened/" + artist
    list_titles(artist, current_directory)


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