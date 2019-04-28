from datetime import datetime


def yt_to_py(yt_datetime):
    pass


def py_to_yt(py_datetime):
    s = py_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')
    return s[:-3]+"Z"


def get_default_ytdate():
    t = datetime(1970, 1, 1)
    return py_to_yt(t)


def get_current_ytdate():
    return py_to_yt(datetime.now())
