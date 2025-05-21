from os import path
from time import sleep
from .config import *
from .drive import init_drive
from .sync import sync_folder


def validate(config: Config) -> None:
    if len(config.device_name) == 0:
        raise ValueError('{} cannot be empty.'.format(CONFIG_KEY_DEVICE))
    if len(config.source_dir) == 0:
        raise ValueError('{} cannot be empty.'.format(CONFIG_KEY_SOURCE))
    if len(config.target_dir) == 0:
        raise ValueError('{} cannot be empty.'.format(CONFIG_KEY_TARGET))
    if not path.exists(config.source_dir):
        raise ValueError('Source directory {} does not exist.'.format(config.source_dir))


def run(config: Config) -> None:
    validate(config)
    drive = init_drive(config.device_name)
    source = config.source_dir
    target = path.join(drive.path, config.target_dir)
    try:
        while True:
            sync_folder(source, target)
            print('Re-sync in 60s\n\n')
            sleep(60)
    except KeyboardInterrupt:
        print('\nStop running\n')
    return


def run_cmd() -> None:
    config = Config.load(create_template=True)
    if config is not None:
        run(config)
    return
