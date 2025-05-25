from typing import Mapping, Any

from dataclasses import dataclass
from json import load, dump
from os import path, makedirs
from pathlib import Path

CONFIG_KEY_DEVICE = 'usbName'
CONFIG_KEY_SOURCE = 'source'
CONFIG_KEY_TARGET = 'target'

_config_home_dir = path.join(Path.home(), '.config', 'simple-usb-sync')
_config_home_path = path.join(_config_home_dir, 'config.json')
_config_documents_path = path.join(Path.home(), 'Documents', 'simple-usb-sync.json')
_config_paths = (
    _config_home_path,
    _config_documents_path,
)

@dataclass(frozen=True)
class Config(object):
    device_name: str
    source_dir: str
    target_dir: str

    @classmethod
    def load(cls, create_template: bool=False) -> 'Config':
        config_json = cls._get_config_json(create_template)
        device_name = cls._get_prop(config_json, CONFIG_KEY_DEVICE)
        source_dir = cls._get_prop(config_json, CONFIG_KEY_SOURCE)
        target_dir = cls._get_prop(config_json, CONFIG_KEY_TARGET)
        config = Config(device_name=device_name, source_dir=source_dir, target_dir=target_dir)
        return config
    
    def save(self, path: str=_config_home_path) -> None:
        json = {
            'usbName': self.device_name,
            'source': self.source_dir,
            'target': self.target_dir,
        }
        makedirs(_config_home_dir, exist_ok=True)
        with open(path, 'w') as f:
            dump(json, f, indent=2)
        return
    
    @classmethod
    def _get_config_json(cls, create_template: bool=False) -> Mapping[str, str | None]:
        for config_path in _config_paths:
            if path.exists(config_path):
                with open(config_path, 'r') as f:
                    return load(f)
        if create_template:
            template_config = Config(
                device_name='source to sync',
                source_dir='/absolute/path/to/usb/drive',
                target_dir='relative/path/to/target/folder/in/usbDrive'
            )
            template_config.save(_config_documents_path)
            print('A template config is generated at {}. Please update it.'.format(_config_documents_path))
            exit(0)
        return {}
    
    @classmethod
    def _get_prop(cls, json: Mapping[str, str | None], key: str) -> str:
        if key in json:
            value = json[key]
            return value if value is not None else ""
        return ""
    
    def __str__(self) -> str:
        return 'Config(device_name={}, source={}, target={})'.format(
            self.device_name,
            self.source_dir,
            self.target_dir,
        )
