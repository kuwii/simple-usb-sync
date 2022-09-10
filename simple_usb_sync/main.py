from os import path
from time import sleep
from .config import Config, init_config
from .drive import Drive, init_drive
from .sync import sync_folder


def run(config: Config) -> None:
    drive = init_drive(config.path())
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
