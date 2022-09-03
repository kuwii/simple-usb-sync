from typing import Text
from os import path as os_path, remove, utime
from platform import system
from shutil import rmtree, copy, copy2
from subprocess import run


def get_mtime(file_path: Text) -> float:
    if not os_path.exists(file_path):
        return 0.0
    return os_path.getmtime(file_path)


def copy_file(source: Text, target: Text) -> None:
    print(' - Copy to {}'.format(target))
    # can't use copy2 because it does not always work
    mtime = get_mtime(source)
    copy(source, target)
    utime(target, (mtime, mtime))
    return


def delete(path: Text) -> None:
    if os_path.isdir(path):
        rmtree(path)
    else:
        remove(path)
    return


def should_ignore(filename: Text) -> None:
    if filename.startswith('.'):
        return True
    return False
