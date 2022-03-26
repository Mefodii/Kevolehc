import time
from utils.File import list_files, append_creation_time


COMICS_PATH = "D:/Книги/Comics"
THE_CUMMONER_PATH = "/".join([COMICS_PATH, "The Cummoner [raw]"])


#######################################################################################################################
# Main function
#######################################################################################################################
def __main__():
    files = list_files(THE_CUMMONER_PATH)
    append_creation_time(files)


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