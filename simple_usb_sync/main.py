from os import path
from time import sleep
from .config import Config, get_config, write_config, config_path_documents
from .drive import Drive, get_drive
from .sync import sync_folder


def init_config() -> Config | None:
    config = get_config()
    if config is None:
        write_config(config_path_documents)
        print('A template config is generated at {}. Please update it.'.format(config_path_documents))
        return None
    message = [
        'Using config at {}'.format(config.path()),
        ' - Source: {}'.format(config.source()),
        ' - USB drive: {}'.format(config.usb_name()),
        ' - Target folder: {}'.format(config.target()),
    ]
    print('{}\n'.format('\n'.join(message)))
    return config


def init_drive(config: Config) -> Drive:
    drive_name = config.usb_name()
    drive = None
    while drive is None:
        print('Checking drive {} ... '.format(drive_name))
        drive = get_drive(drive_name)
        if drive is None:
            print('Drive {} is not plugged in\n'.format(drive_name))
            sleep(10)
    print('Drive {} plugged in, mounted at {}\n'.format(drive_name, drive.path()))
    return drive


def run(config: Config) -> None:
    drive = init_drive(config)
    source = config.source()
    target = path.join(drive.path(), config.target())
    try:
        while True:
            sync_folder(source, target)
            print('Re-sync in 60s\n\n')
            sleep(60)
    except KeyboardInterrupt:
        print('\nStop running\n')
    return



def main() -> None:
    config = init_config()
    if config is not None:
        run(config)
    return
