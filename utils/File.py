from os import listdir
from os.path import isfile, join, isdir
import codecs
import os
import glob
import json
import time

from stat import S_ISREG, ST_CTIME, ST_MODE

PATH = "path"
FILENAME = "filename"
EXTENSION = "extension"
CR_TIME = "cr_time"
CR_TIME_READABLE = "cr_time_r"


# Read file
def get_file_lines(file_name, utf=None):
    if utf:
        input_file = codecs.open(file_name, 'r', "utf-" + str(utf))
    else:
        input_file = open(file_name, 'r')

    data = []
    for input_line in input_file:
        data.append(input_line.replace("\n", ""))
    return data


# Read file which is a JSON
def get_json_data(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)


def write_json_data(file_path, json_data):
    with open(file_path, 'w') as outfile:
        json.dump(json_data, outfile, sort_keys=True, indent=4)


# Write to file
def write_lines_to_file(file_name, file_text):
    result_file = open(file_name, 'w')
    for result_line in file_text:
        result_file.write(str(result_line) + "\n")
    result_file.close()


# Write to file in utf-8 format
def write_lines_to_file_utf8(file_name, file_text):
    result_file = codecs.open(file_name, 'w', "utf-8")
    for result_line in file_text:
        result_file.write(str(result_line) + "\n")
    result_file.close()


# Append a list of lines to an already existing file.
# If file does not exist, create it.
def append_to_file(file_name, file_text):
    result_file = codecs.open(file_name, 'a+', "utf-8")
    if isinstance(file_text, list):
        for result_line in file_text:
            result_file.write(str(result_line) + "\n")
    else:
        result_file.write(str(file_text) + "\n")
    result_file.close()


def get_file_name_with_extension(path, name):
    for infile in glob.glob(os.path.join(path, name + '.*')):
        return infile


# Check if file exists
def exists(file_path):
    flag = os.path.isfile(file_path)
    if flag:
        return True
    return False


# Delete file
def delete(file_path):
    os.remove(file_path)


# Return a list of files from specified path (files inside folders of this path are not checked)
# Format:
#   {
#       "path": path,
#       "filename": filename.extension
#   }
def list_files(path, with_creation_time=False):
    files = [{PATH: path, FILENAME: f, EXTENSION: f.split(".")[-1]} for f in listdir(path) if isfile(join(path, f))]
    if with_creation_time:
        append_creation_time(files)
    return files


# Return a list of folders from specified path (folders inside folders of this path are not checked)
def list_dirs(path):
    return [join(path, f) for f in listdir(path) if isdir(join(path, f))]


# Append file creation time for each received file
# Format:
#   {
#       ...
#       "created": file_creation_time
#   }
def append_creation_time(files: list):
    for file in files:
        for key in [PATH, FILENAME]:
            if key not in file:
                raise ValueError(f'Key: {key}. Missing from dict definition')

        abs_path = join(file[PATH], file[FILENAME])
        creation_time = os.path.getctime(abs_path)
        file[CR_TIME] = creation_time
        file[CR_TIME_READABLE] = time.ctime(creation_time)
    return []


# Return a list of files from specified path. Files in subdirectories as well.
# Format:
#   {
#       "path": path,
#       "filename": filename.extension
#   }
def list_files_sub(path):
    data = list_files(path)

    for directory in list_dirs(path):
        data += list_files_sub(directory)

    return data
