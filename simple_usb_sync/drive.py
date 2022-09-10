from typing import Text, Sequence, Mapping
from os import path, listdir
from platform import system
from time import sleep


class Drive(object):
    def __init__(self, drive_name: Text, drive_path: Text) -> None:
        self._name = str(drive_name)
        self._path = str(drive_path)
        return

    def name(self) -> Text:
        return self._name

    def path(self) -> Text:
        return self._path


class Drives(object):
    def __init__(self) -> None:
        os_type = system().lower()
        if os_type == 'darwin':
            self._drives = self._macos_init()
        else:
            raise NotImplemented("Your OS platform {} is not supported yet.".format(os_type))
        return

    def list(self) -> Sequence[Drive]:
        return list(self._drives.values())

    def has(self, drive_name: Text) -> bool:
        return drive_name in self._drives

    def get(self, drive_name: Text) -> Drive:
        return self._drives[drive_name]

    def _macos_init(_) -> Mapping[Text, Drive]:
        home = '/Volumes'
        names = listdir(home)
        drives = ((name, Drive(name, path.join(home, name))) for name in names)
        mapping = dict(drives)
        return mapping


def get_drive(drive_name: Text) -> Drive | None:
    drives = Drives()
    if drives.has(drive_name):
        return drives.get(drive_name)
    return None


def init_drive(drive_name: Text) -> Drive:
    drive = None
    while drive is None:
        print('Checking drive {} ... '.format(drive_name))
        drive = get_drive(drive_name)
        if drive is None:
            print('Drive {} is not plugged in\n'.format(drive_name))
            sleep(10)
    print('Drive {} plugged in, mounted at {}\n'.format(drive_name, drive.path()))
    return drive
