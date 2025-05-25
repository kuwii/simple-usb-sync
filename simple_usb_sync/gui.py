from typing import Callable, Any

from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import path
from threading import Thread, current_thread
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from time import sleep

from .config import Config
from .drive import Drive, get_drive
from .sync import sync_folder


STYLE_LABEL_NORMAL = 'TLabel'
STYLE_LABEL_ERROR = 'error.TLabel'
STYLE_BUTTON_NORMAL = 'TButton'
STYLE_BUTTON_RUNNING = 'running.TButton'
STYLE_BUTTON_DISABLE = 'disable.TButton'

TEXT_BUTTON_AUTO = 'Auto Sync'
TEXT_BUTTON_SYNC = 'Sync Now'
TEXT_BUTTON_EXIT = 'Exit'

class StringInput(object):
    def __init__(self, frame: ttk.Frame, name: str):
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, pady=2)
        label = ttk.Label(row, text=name, width=14, anchor='w', style=STYLE_LABEL_NORMAL)
        label.pack(side=tk.LEFT, padx=(0, 10))
        entry = ttk.Entry(row)
        entry.pack(fill=tk.X, expand=True)
        self._name = name
        self._label = label
        self._entry = entry
        return

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> str:
        value = self._entry.get()
        return value if value is not None else ""

    def set_value(self, value: str) -> None:
        self._entry.delete(0, 'end')
        self._entry.insert(0, value)

    def set_normal(self) -> None:
        self._label.configure(style=STYLE_LABEL_NORMAL)
        return

    def set_error(self) -> None:
        self._label.configure(style=STYLE_LABEL_ERROR)
        return

    def validate(self) -> list[str]:
        if len(self.value) == 0:
            self.set_error()
            return ['Input "{}" cannot be empty.'.format(input.name)]
        else:
            self.set_normal()
            return []


class Button(object):
    def __init__(self,
                 frame: ttk.Frame,
                 name: str,
                 command: None | Callable[[], Any]=None):
        button = ttk.Button(frame, text=name, command=(command if command is not None else ""))
        button.pack(fill=tk.X, pady=2)
        self._button = button
        return

    def set_name(self, name: str) -> None:
        self._button.configure(text=name)

    def set_normal(self) -> None:
        self._button.configure(state=tk.NORMAL)

    def set_disable(self) -> None:
        self._button.configure(state=tk.DISABLED)


class PathInput(StringInput):
    def __init__(self, frame: ttk.Frame, name: str):
        super().__init__(frame, name)

    def validate(self) -> list[str]:
        errors = super().validate()
        if len(errors) == 0 and (not path.exists(self.value)):
            self.set_error()
            errors.append('Path {} does not exist'.format(self.value))
        return errors


class SyncRunner(ABC):
    def __init__(self, validate_fn: Callable[[], list[str]]):
        super().__init__()
        self._validate_fn = validate_fn

    def is_plugged_in(self, config: Config) -> bool:
        drive_name = config.device_name
        drive = get_drive(drive_name)
        if drive is None:
            return False
        return True

    def validate(self, config: Config) -> bool:
        errors = self._validate_fn()
        if len(errors) > 0:
            err_msg = '\n'.join(errors)
            messagebox.showerror('Error', err_msg)
            return False
        return True

    def start(self, config: Config) -> None:
        self.lock()
        if not self.validate(config):
            print('Validate failed. Skip.')
            self.unlock()
            return
        print('Validate passed. Save config ...')
        config.save()
        print('Start thread to sync ...')
        thread = Thread(target=self.sync, args=(config,), daemon=True)
        thread.start()
        self._thread = thread
        return

    @abstractmethod
    def lock(self) -> None:
        return

    @abstractmethod
    def unlock(self) -> None:
        return

    @abstractmethod
    def sync(self, config: Config) -> None:
        pass


class ManualSyncRunner(SyncRunner):
    def __init__(self,
                 btn_auto: Button,
                 btn_sync: Button,
                 validate_fn: Callable[[], list[str]]):
        super().__init__(validate_fn)
        self._btn_auto = btn_auto
        self._btn_sync = btn_sync

    def validate(self, config: Config) -> bool:
        if not super().validate(config):
            return False
        if not self.is_plugged_in(config):
            messagebox.showerror('Error', 'USB drive {} is not plugged in.'.format(config.device_name))
            return False
        return True

    def lock(self) -> None:
        self._btn_auto.set_name('Syncing ...')
        self._btn_auto.set_disable()
        self._btn_sync.set_name('Syncing ...')
        self._btn_sync.set_disable()
        return

    def unlock(self) -> None:
        self._btn_auto.set_name(TEXT_BUTTON_AUTO)
        self._btn_auto.set_normal()
        self._btn_sync.set_name(TEXT_BUTTON_SYNC)
        self._btn_sync.set_normal()
        return

    def sync(self, config: Config) -> None:
        drive_name = config.device_name
        drive = get_drive(drive_name)
        source_path = config.source_dir
        target_path = path.join(drive.path, config.target_dir)
        sync_folder(source_path, target_path)
        messagebox.showinfo('Complete', 'Done')
        self.unlock()
        return


class AutoSyncRunner(SyncRunner):
    def __init__(self,
                 btn_auto: Button,
                 btn_sync: Button,
                 validate_fn: Callable[[], list[str]]):
        super().__init__(validate_fn)
        self._btn_auto = btn_auto
        self._btn_sync = btn_sync
        self._remaining_seconds = 60
        self._running = False
        self._stop = False
        return

    def lock(self) -> None:
        if not self._running:
            self._running = True
            self._btn_auto.set_name('Stop Sync')
            self._btn_sync.set_name('Auto Syncing ...')
            self._btn_sync.set_disable()
        else:
            self._stop = True
            self._btn_auto.set_name('Stopping Auto Sync ...')
            self._btn_auto.set_disable()
            self._btn_sync.set_name('Stopping Auto Sync ...')
            self._btn_sync.set_disable()
        return

    def unlock(self) -> None:
        self._running = False
        self._stop = False
        self._btn_auto.set_name(TEXT_BUTTON_AUTO)
        self._btn_auto.set_normal()
        self._btn_sync.set_name(TEXT_BUTTON_SYNC)
        self._btn_sync.set_normal()
        return

    def sync(self, config: Config) -> None:
        if self._stop:
            self.stop()
        elif self._running:
            self.auto_sync(config)
        return

    def auto_sync(self, config: Config) -> None:
        print('Start auto sync ...')
        msg, count = self._run(config)
        while self._running:
            print(' - [subthread] Running: {} | Stop: {} | Count: {}'.format(self._running, self._stop, count))
            if count == 0:
                msg, count = self._run(config)
            else:
                self._btn_sync.set_name('{} in {} seconds ...'.format(msg, count))
                count -= 1
            sleep(1)
        print('Auto sync stopped.')
        self.unlock()

    def stop(self) -> None:
        print('Stop auto sync ...')
        self._running = False
        return

    def _run(self, config: Config) -> tuple[str, int]:
        self._btn_sync.set_name('Syncing ...')
        if not self.is_plugged_in(config):
            return ('Not plugged in. Re-check', 10,)
        else:
            drive_name = config.device_name
            drive = get_drive(drive_name)
            source_path = config.source_dir
            target_path = path.join(drive.path, config.target_dir)
            sync_folder(source_path, target_path)
            return ('Sync complete. Re-sync', 60,)


class GUI(object):
    def __init__(self):
        self._lock = False

        self._root = tk.Tk()
        self._root.title('Simple USB Sync')
        self._root.geometry('500x240')
        self._root_frm = ttk.Frame(self._root, padding=20)
        self._root_frm.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style(self._root_frm)
        style.configure(STYLE_LABEL_ERROR, foreground='red')

        self._input_drive = StringInput(self._root_frm, 'USB Drive Name')
        self._input_source_dir = PathInput(self._root_frm, 'Source')
        self._input_target_dir= StringInput(self._root_frm, 'Target')

        self._btn_auto = Button(self._root_frm, TEXT_BUTTON_AUTO, command=self._auto_sync)
        self._btn_sync = Button(self._root_frm, TEXT_BUTTON_SYNC, command=self._sync)
        self._btn_exit = Button(self._root_frm, TEXT_BUTTON_EXIT, command=self._exit)

        config = Config.load()
        self._input_drive.set_value(config.device_name)
        self._input_source_dir.set_value(config.source_dir)
        self._input_target_dir.set_value(config.target_dir)
        self._validate()

        self._manual_sync_runner = ManualSyncRunner(self._btn_auto, self._btn_sync, self._validate)
        self._auto_sync_runner = AutoSyncRunner(self._btn_auto, self._btn_sync, self._validate)

        return

    def run(self) -> None:
        self._root.mainloop()
        return

    def _exit(self) -> None:
        self._auto_sync_runner.stop()
        self._root.destroy()
        return

    def _auto_sync(self) -> None:
        config = self._get_config()
        self._auto_sync_runner.start(config)
        return

    def _sync(self) -> None:
        config = self._get_config()
        self._manual_sync_runner.start(config)
        return

    def _validate(self) -> list[str]:
        errors = []
        errors += self._input_drive.validate()
        errors += self._input_source_dir.validate()
        errors += self._input_target_dir.validate()
        return errors

    def _get_config(self) -> Config:
        device_name = self._input_drive.value
        source_dir = self._input_source_dir.value
        target_dir = self._input_target_dir.value
        config = Config(device_name=device_name, source_dir=source_dir, target_dir=target_dir)
        return config


def run_gui():
    gui = GUI()
    gui.run()
