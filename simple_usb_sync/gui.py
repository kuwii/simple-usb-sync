from typing import Callable, Any

from dataclasses import dataclass
from os import path
from threading import Thread
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from .config import Config
from .drive import Drive, get_drive
from .sync import sync_folder


STYLE_LABEL_NORMAL = 'TLabel'
STYLE_LABEL_ERROR = 'error.TLabel'
STYLE_BUTTON_NORMAL = 'TButton'
STYLE_BUTTON_RUNNING = 'running.TButton'
STYLE_BUTTON_DISABLE = 'disable.TButton'


@dataclass(init=False, frozen=True)
class StringInput(object):
    name: str
    label: ttk.Label
    entry: ttk.Entry

    def __init__(self, frame: ttk.Frame, name: str):
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, pady=2)
        label = ttk.Label(row, text=name, width=14, anchor='w', style=STYLE_LABEL_NORMAL)
        label.pack(side=tk.LEFT, padx=(0, 10))
        entry = ttk.Entry(row)
        entry.pack(fill=tk.X, expand=True)
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'label', label)
        object.__setattr__(self, 'entry', entry)
        return
    
    @property
    def value(self) -> str:
        value = self.entry.get()
        return value if value is not None else ""
    
    def set_normal(self) -> None:
        self.label.configure(style=STYLE_LABEL_NORMAL)
        return

    def set_error(self) -> None:
        self.label.configure(style=STYLE_LABEL_ERROR)
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
        

@dataclass(init=False, frozen=True)
class PathInput(StringInput):
    def __init__(self, frame: ttk.Frame, name: str):
        super().__init__(frame, name)

    def validate(self) -> list[str]:
        errors = super().validate()
        if len(errors) == 0 and (not path.exists(self.value)):
            self.set_error()
            errors.append('Path {} does not exist'.format(self.value))
        return errors


class GUI(object):
    def __init__(self):
        self._lock = False

        self._root = tk.Tk()
        self._root.title('Simple USB Sync')
        self._root.geometry('500x200')
        self._root_frm = ttk.Frame(self._root, padding=20)
        self._root_frm.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style(self._root_frm)
        style.configure(STYLE_LABEL_ERROR, foreground='red')

        self._input_drive = StringInput(self._root_frm, 'USB Drive Name')
        self._input_source_dir = PathInput(self._root_frm, 'Source')
        self._input_target_dir= StringInput(self._root_frm, 'Target')

        self._btn_sync = Button(self._root_frm, 'Sync Now', command=self._sync)
        self._btn_exit = Button(self._root_frm, 'Exit', command=self._exit)

        config = Config.load()
        self._input_drive.entry.insert(0, config.device_name)
        self._input_source_dir.entry.insert(0, config.source_dir)
        self._input_target_dir.entry.insert(0, config.target_dir)
        self._validate()

        return

    def run(self) -> None:
        self._root.mainloop()
        return
    
    def _exit(self) -> None:
        if not self._lock:
            self._root.destroy()
        else:
            messagebox.showerror('Error', 'Still syncing. Please don\'t exit.')
        return

    def _sync(self) -> None:
        self._lock_sync()
        errors = self._validate()
        if len(errors) > 0:
            err_msg = '\n'.join(errors)
            messagebox.showerror('Error', err_msg)
            self._unlock_sync()
            return
        
        drive_name = self._input_drive.value
        drive = get_drive(drive_name)
        if drive is None:
            messagebox.showerror('Error', 'USB drive {} is not plugged in.'.format(drive_name))
            self._unlock_sync()
            return

        self._save_config()

        thread = Thread(target=self._do_sync, args=(drive,))
        thread.start()

        return
    
    def _validate(self) -> list[str]:
        errors = []
        errors += self._input_drive.validate()
        errors += self._input_source_dir.validate()
        errors += self._input_target_dir.validate()
        return errors
    
    def _lock_sync(self) -> None:
        self._lock = True
        self._btn_sync.set_name('Syncing ...')
        self._btn_sync.set_disable()

    def _unlock_sync(self) -> None:
        self._lock = False
        self._btn_sync.set_name('Sync Now')
        self._btn_sync.set_normal()
    
    def _save_config(self) -> None:
        device_name = self._input_drive.value
        source_dir = self._input_source_dir.value
        target_dir = self._input_target_dir.value
        cur_config = Config(device_name=device_name, source_dir=source_dir, target_dir=target_dir)
        prev_config = Config.load()
        if cur_config != prev_config:
            cur_config.save()
            print('{} saved.'.format(cur_config))
        return
    
    def _do_sync(self, drive: Drive) -> None:
        source_path = self._input_source_dir.value
        target_path = path.join(drive.path, self._input_target_dir.value)
        sync_folder(source_path, target_path)
        messagebox.showinfo('Complete', 'Done')
        self._unlock_sync()
        return


def run_gui():
    gui = GUI()
    gui.run()
