# Simple USB Sync

A simple, stupid, configuration-based tool for automatically syncing files to a specific USB drive.

## Features

Made for those who only need to automatically copy files without other requirement.

- Sync 2 folders. One at arbitrary location, one in a USB drive with specified name.
- Runs every 60 seconds. Only sync if the specified USB drive is plugged in.
- Ignore files that has leading `.` in filename.
- No parameters, no lock, no other complex features - just copy files.

## Requirements

Only Python3 is needed. But if it is installed by Homebrew, `python-tk` is also needed.

## How to build

To build the wheel, [build](https://github.com/pypa/build) should be installed first.

Then run `python -m build`. The whl file will be created in `dist` folder.

## How to Install

Download a [release](https://github.com/kuwii/simple-usb-sync/releases), and install it through `pip`.

## How to use

After installation, 4 commands will be available:

- `simple-usb-sync` and `usbsync` will run sync in terminal.
- `simple-usb-sync-gui` and `usbsync-gui` will open a GUI version of the program.

The program will try to read config from these 2 locations, any one of which can work:

- `~/.config/simple-usb-sync/config.json` (used first)
- `~/Documents/simple-usb-sync.json`

If neither of these 2 configs exists, the program will leave a config template at `~/Documents/simple-usb-sync.json`. Please open and update the items, including:

- `source`: The folder to sync to USB drive.
- `usbName`: Name of the USB drive showed in file explorer.
- `target`: Folder name in USB drive to store the synced files.

After the config updated, just run the program again. No parameter needed and supported.

## Supported platforms

- macOS

## To do

- Windows support
- Linux support
- Parallel file copy
- Pip install
