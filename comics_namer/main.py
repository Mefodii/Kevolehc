import time
import os
from datetime import datetime

from utils import file
from utils.file import list_files, CR_TIME, FILENAME, PATH, EXTENSION
from constants.paths import DB_FILE

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

COMICS_PATH = "H:/Книги/Comics"
MANGA_PATH = "H:/Книги/Manga"
TEMP_PATH = COMICS_PATH + "/temp"

COMIC_NAME = "name"
COMIC_PATH = "path"
COMIC_PAGES_NR = "pages"
COMIC_CREATION_DATE = "creation_date"
COMIC_MOD_DATE = "modification_date"

C_THE_CUMMONER = "The Cummoner"
C_OGLAF = "Oglaf"
C_CASSIOPEIA_QUINN = "Cassiopeia Quinn"
C_IROVEDOUT = "I Roved Out"
C_ALFIE = "Alfie"


def get_current_date():
    return datetime.utcnow().strftime(DATE_FORMAT)[:-3]+"Z"


def add_new_comic(comic_path, comic_name):
    db_json = {}
    if file.exists(DB_FILE):
        db_json = file.read_json(DB_FILE)

    if db_json.get(comic_name, None):
        raise Exception(f"Comic with name: {comic_name} already exists. Unable to insert")

    db_json[comic_name] = {
        COMIC_NAME: comic_name,
        COMIC_PATH: comic_path,
        COMIC_PAGES_NR: 0,
        COMIC_CREATION_DATE: get_current_date(),
        COMIC_MOD_DATE: get_current_date(),
    }

    file.write_json(DB_FILE, db_json)


def sync_pages_name(comic_name, keep_old_name=True):
    if not file.exists(DB_FILE):
        raise Exception(f"DB_FILE does not exist: {DB_FILE}")

    db_json = file.read_json(DB_FILE)
    if not db_json.get(comic_name, None):
        raise Exception(f"Comic with name: {comic_name} does not exist.")

    comic = db_json.get(comic_name)
    comic_path = comic.get(COMIC_PATH)
    pages_nr = comic.get(COMIC_PAGES_NR)

    files = list_files(comic_path, with_creation_time=True)
    # To change creation date in powershell use command:
    #   (Get-Item "C:\Users\mefod\Downloads\p3-2.jpg").CreationTime=("21 April 2022 07:00:02")
    files = sorted(files, key=lambda f: f.cr_time)

    rename_files(files[pages_nr:], comic_name, pages_nr + 1, keep_old_name)

    comic[COMIC_PAGES_NR] = pages_nr
    comic[COMIC_MOD_DATE] = get_current_date()

    file.write_json(DB_FILE, db_json)


def rename_temp_files(comic_name, initial_page_number=1, keep_old_name=True):
    files = list_files(TEMP_PATH, with_creation_time=True)
    # To change creation date in powershell use command:
    #   (Get-Item "C:\Users\mefod\Downloads\p3-2.jpg").CreationTime=("21 April 2022 07:00:02")
    files = sorted(files, key=lambda f: f.cr_time)
    rename_files(files, comic_name, initial_page_number, keep_old_name)


def rename_files(files, comic_name, initial_page_number, keep_old_name=True):
    pages_nr = initial_page_number
    for item in files:
        path = item[PATH]
        old_name = item[FILENAME]
        new_name = f"{comic_name} - {pages_nr:04d}"
        if keep_old_name:
            new_name = f"{new_name} - {old_name}"
        else:
            new_name += f".{item[EXTENSION]}"

        old_abs_name = "\\".join([path, old_name])
        new_abs_name = "\\".join([path, new_name])

        print(f"Renaming: {old_name}, to: {new_name}")
        os.rename(old_abs_name, new_abs_name)
        pages_nr += 1


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    # add_new_comic(COMICS_PATH + "/Alfie [raw]", C_ALFIE)
    # sync_pages_name(C_IROVEDOUT)
    # sync_pages_name(C_OGLAF)
    # sync_pages_name(C_CASSIOPEIA_QUINN)
    # sync_pages_name(C_THE_CUMMONER)
    # sync_pages_name(C_ALFIE)
    # rename_temp_files("Brandon Sanderson - White Sand 3", 1, False)
    rename_temp_files("Brandon Sanderson - Dark One 1", 1, False)
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
