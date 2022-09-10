from typing import Text, Any
from os import path, makedirs
from pathlib import Path
from json import load, dump


config_path_user = path.join(Path.home(), '.config', 'simple-usb-sync', 'config.json')
config_path_documents = path.join(Path.home(), 'Documents', 'simple-usb-sync.json')

default_config = {
    'source': '<source to sync>',
    'usbName': '<name of usb drive>',
    'target': '<name of target folder in usb drive>',
}


class Config(object):
    def __init__(self, config_path: Text):
        self._path = str(config_path)
        with open(self._path, 'r') as f:
            config = load(f)
        self._check(config)
        self._source = str(config['source'])
        self._usbName = str(config['usbName'])
        self._target = str(config['target'])
        return

    def path(self) -> Text:
        return self._path

    def source(self) -> Text:
        return self._source

    def usb_name(self) -> Text:
        return self._usbName

    def target(self) -> Text:
        return self._target

    def _check(self, config_json: Any) -> None:
        for key in ['source', 'usbName', 'target']:
            if config_json[key] == default_config[key]:
                raise RuntimeError('Config in {} not set'.format(self._path))
        return


def get_config() -> Config | None:
    if path.exists(config_path_user):
        return Config(config_path_user)
    if path.exists(config_path_documents):
        return Config(config_path_documents)
    return None


def write_config(config_path: Text, config: Any) -> None:
    config_dir = path.dirname(config_path)
    if not path.exists(config_dir):
        makedirs(config_dir)
    with open(config_path, 'w') as f:
        dump(config, f, indent=2)
        f.write('\n')
    return


def init_config() -> Config | None:
    config = get_config()
    if config is None:
        write_config(config_path_documents, default_config)
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
