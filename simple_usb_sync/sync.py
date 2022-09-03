from typing import Text
from os import path, mkdir, listdir
from .fs import get_mtime, copy_file, delete, should_ignore


def sync_file(source: Text, target: Text) -> None:
    print('Syncing file: {}'.format(source))
    # delete target if it is a folder
    if path.isdir(target):
        delete(target)
    # get last modified time, only copy if source is updated
    source_mtime = int(get_mtime(source) * 100)
    target_mtime = int(get_mtime(target) * 100)
    if source_mtime != target_mtime:
        copy_file(source, target)
    else:
        print(' - Same file')
    print('')
    return


def sync_folder(source: Text, target: Text) -> None:
    print('Syncing folder: {}'.format(source))
    # create target folder if it does not exist
    if not path.exists(target):
        mkdir(target)
    # delete target if it is not a folder
    if path.isfile(target):
        print(' - Delete: {}'.format(target))
        delete(target)
    source_items = list(filter(lambda x: not should_ignore(x), listdir(source)))
    target_items = listdir(target)
    # delete target items that is not in source
    for it in target_items:
        if it not in source_items:
            delete(path.join(target, it))
    print('')
    # sync source items in folder
    for it in source_items:
        source_path = path.join(source, it)
        target_path = path.join(target, it)
        if path.isdir(source_path):
            sync_folder(source_path, target_path)
        else:
            sync_file(source_path, target_path)
    return
