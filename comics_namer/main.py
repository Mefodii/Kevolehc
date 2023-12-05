import time
import os
from datetime import datetime
from typing import Self

from utils import file
from utils.file import list_files, File
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


class Comic:
    def __init__(self, name: str, path: str, pages: int, cr_date: str, mod_date: str):
        self.name = name
        self.path = path
        self.pages = pages
        self.cr_date = cr_date
        self.mod_date = mod_date

    @classmethod
    def new(cls, comic_name: str, comic_path: str) -> Self:
        new_date = get_current_date()
        return cls(comic_name, comic_path, 0, new_date, new_date)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        name = data.get(COMIC_NAME)
        path = data.get(COMIC_PATH)
        pages = data.get(COMIC_PAGES_NR)
        cr_date = data.get(COMIC_CREATION_DATE)
        mod_date = data.get(COMIC_MOD_DATE)

        obj = cls(name, path, pages, cr_date, mod_date)
        return obj

    def to_dict(self):
        data = {
            COMIC_NAME: self.name,
            COMIC_PATH: self.path,
            COMIC_PAGES_NR: self.pages,
            COMIC_CREATION_DATE: self.cr_date,
            COMIC_MOD_DATE: self.mod_date,
        }

        return data

    def sync_pages_name(self, keep_old_name=True):
        files = list_files(self.path, with_creation_time=True)
        # To change creation date in powershell use command:
        #   (Get-Item "C:\Users\mefod\Downloads\p3-2.jpg").CreationTime=("21 April 2022 07:00:02")
        files = sorted(files, key=lambda f: f.cr_time)

        new_pages = len(files)
        if self.pages == new_pages:
            print(f"{self.name} - has no new pages. Skipped")
            return

        if self.pages > new_pages:
            msg = (f"{self.name} - unable to sync. Comic has pages value higher than total files len. "
                   f"Pages: {self.pages}. Files: {new_pages}")
            raise Exception(msg)

        rename_files(files[self.pages:], self.name, self.pages + 1, keep_old_name)

        print(f"{self.name} - added {new_pages - self.pages} pages")
        self.pages = len(files)
        self.mod_date = get_current_date()


class ComicDict:

    def __init__(self, data: dict[str, Comic]):
        self.comics = data

    @classmethod
    def from_file(cls, file_path: str) -> Self:
        data = file.read_json(file_path)
        comics = [Comic.from_dict(v) for v in data]
        return cls({comic.name: comic for comic in comics})

    def write(self, file_path: str) -> None:
        data = [v.to_dict() for k, v in self.comics.items()]
        file.write_json(file_path, data)

    def add_new(self, comic_name: str, comic_path: str):
        if self.comics.get(comic_name):
            raise Exception(f"Comic with name: {comic_name} already exists. Unable to insert")

        self.comics[comic_name] = Comic.new(comic_name, comic_path)


def get_current_date():
    return datetime.utcnow().strftime(DATE_FORMAT)[:-3]+"Z"


def rename_temp_files(comic_name, initial_page_number=1, keep_old_name=True):
    files = list_files(TEMP_PATH, with_creation_time=True)
    # To change creation date in powershell use command:
    #   (Get-Item "C:\Users\mefod\Downloads\p3-2.jpg").CreationTime=("21 April 2022 07:00:02")
    files = sorted(files, key=lambda f: f.cr_time)
    rename_files(files, comic_name, initial_page_number, keep_old_name)


def rename_files(files: list[File], comic_name: str, initial_page_number: int, keep_old_name=True):
    pages_nr = initial_page_number
    for item in files:
        path = item.path
        old_name = item.name
        new_name = f"{comic_name} - {pages_nr:04d}"
        if keep_old_name:
            new_name = f"{new_name} - {old_name}"
        else:
            new_name += f".{item.extension}"

        old_abs_name = "\\".join([path, old_name])
        new_abs_name = "\\".join([path, new_name])

        print(f"Renaming: {old_name}, to: {new_name}")
        os.rename(old_abs_name, new_abs_name)
        pages_nr += 1


def sync_db():
    comics_dict = ComicDict.from_file(DB_FILE)
    comics = comics_dict.comics
    [c.sync_pages_name() for c in comics.values()]
    comics_dict.write(DB_FILE)


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    # add_new_comic(COMICS_PATH + "/Alfie [raw]", C_ALFIE)
    # sync_pages_name(C_IROVEDOUT)
    # rename_temp_files("Brandon Sanderson - White Sand 3", 1, False)
    sync_db()
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
