from __future__ import unicode_literals
import time

from icecream import ic

from utils import file
from youtube import paths


def alter_db_kv():
    files = file.list_files(paths.DB_PATH)
    for item in files:
        db_file = item.get_abs_path()
        ic(db_file)

        data = file.read_json(db_file)

        # change DB keys and values

        file.write_json(db_file, data)


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    pass


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
