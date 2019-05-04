import os

PROJECT_PATH = "\\".join(os.getcwd().split("\\")[0:-1])
FILES_PATH = PROJECT_PATH + "\\files"
OUTPUT_FILES_PATH = FILES_PATH + "\\output"

INPUT_FILE = "input.txt"
INPUT_FILE_PATH = FILES_PATH + "\\" + INPUT_FILE
