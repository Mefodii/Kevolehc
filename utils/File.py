from os import listdir
from os.path import isfile, join, isdir
import codecs
import os
import glob
import json
import time

from stat import S_ISREG, ST_CTIME, ST_MODE
from typing import Any

PATH = "path"
FILENAME = "filename"
EXTENSION = "extension"
CR_TIME = "cr_time"
CR_TIME_READABLE = "cr_time_r"

ENCODING_UTF8 = "utf-8"


def read(file_name: str, encoding: str = None) -> list[str]:
    """
    Fully read file as list of string
    :param file_name:
    :param encoding:
    :return:
    """
    if encoding:
        input_file = codecs.open(file_name, 'r', encoding)
    else:
        input_file = open(file_name, 'r')

    data = []
    for input_line in input_file:
        data.append(input_line.replace("\n", ""))
    return data


def read_json(file_path: str) -> dict:
    """
    Read file which is in a JSON format
    :param file_path:
    :return: dict representation of file content
    """
    with open(file_path) as json_file:
        return json.load(json_file)


def write_json(output_path: str, data: dict) -> None:
    """
    Dumbs data to the output file in a json format.

    Sorted by keys.

    Indent: 4
    :param output_path:
    :param data:
    :return:
    """
    with open(output_path, 'w') as outfile:
        # Note: 2023.10.23 - unicode output is displayed as "\u***", atm it seems not a good idea to make file readable.
        # src - https://stackoverflow.com/questions/18337407/saving-utf-8-texts-with-json-dumps-as-utf-8-not-as-a-u-escape-sequence
        json.dump(data, outfile, sort_keys=True, indent=4)


def write(output_path: str, data: list[Any], encoding: str = None) -> None:
    """
    Write str representation of each element from "data" to the output_path.

    Line separator: "\\\\n".
    :param output_path:
    :param data:
    :param encoding:
    :return:
    """
    if encoding:
        result_file = codecs.open(output_path, 'w', encoding)
    else:
        result_file = open(output_path, 'w')
    for result_line in data:
        result_file.write(str(result_line) + "\n")
    result_file.close()


def append(output_path: str, data: list[Any] | Any):
    """
    Append str representation of each element from "data" to the output_path.

    If "data" is not a list, then append str representation of "data".

    Line separator: "\\\\n".
    
    Create output_path if it doesn't exist.
    :param output_path:
    :param data:
    :return:
    """
    result_file = codecs.open(output_path, 'a+', ENCODING_UTF8)
    if isinstance(data, list):
        for result_line in data:
            result_file.write(str(result_line) + "\n")
    else:
        result_file.write(str(data) + "\n")
    result_file.close()


def get_file_extension(path: str, name: str) -> str:
    """
    Get the extension of the first file with matches the criteria.

    Raise exception if file not found.
    :param path:
    :param name:
    :return: file extension
    """
    pattern = os.path.join(path, name + '.*')
    for infile in glob.glob(pattern):
        return infile.split(".")[-1]

    raise Exception(f"No file found: {pattern}")


def exists(file_path: str) -> bool:
    """
    :param file_path:
    :return: true if file exists
    """
    return os.path.isfile(file_path)


def delete(file_path: str):
    """
    Delete file from the current system
    :param file_path:
    :return:
    """
    os.remove(file_path)


def list_files(path: str, with_creation_time: bool = False) -> list[dict]:
    """
    Return a list of files from specified path.

    Not recursive

    example: [{ PATH: path, FILENAME: filename, CR_TIME: file_creation_datetime,
    CR_TIME_READABLE: file_creation_datetime_human_readable}]

    :param path:
    :param with_creation_time: True -> append CR_TIME and CR_TIME_READABLE to return elements
    :return:
    """
    files = [{PATH: path, FILENAME: f, EXTENSION: f.split(".")[-1]} for f in listdir(path) if isfile(join(path, f))]
    if with_creation_time:
        append_creation_time(files)
    return files


def list_dirs(path: str) -> list[str]:
    """
    Return a list of folder from specified path in absolute form (path\\\\<result>).

    Not recursive.

    :param path:
    :return:
    """
    return [join(path, f) for f in listdir(path) if isdir(join(path, f))]


def append_creation_time(files: list) -> list:
    """
    Append file creation time for each received file. Mutated.

    example: [{ ..., CR_TIME: x, CR_TIME_READABLE: y }]
    :param files:
    :return:
    """
    for file in files:
        for key in [PATH, FILENAME]:
            if key not in file:
                raise ValueError(f'Key: {key}. Missing from dict definition')

        abs_path = join(file[PATH], file[FILENAME])
        creation_time = os.path.getctime(abs_path)
        file[CR_TIME] = creation_time
        file[CR_TIME_READABLE] = time.ctime(creation_time)
    return []


def list_files_sub(path: str) -> list[dict]:
    """
    Return a list of files from specified path. Recursive.

    example: [{ PATH: path, FILENAME: filename}]
    :param path:
    :return:
    """

    # TODO - probably can be merged with list_files function and to have a argument "recursive=T/F"
    data = list_files(path)

    for directory in list_dirs(path):
        data += list_files_sub(directory)

    return data
