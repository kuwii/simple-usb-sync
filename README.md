# Simple USB Sync

A super simple personal-use tool for automatically syncing files to a specific USB drive.

## Features

Made for those who only need to automatically copy files without other requirement.

- Sync 2 folders. One at arbitrary location, one in a USB drive with specified name.
- Runs every 60 seconds. Only sync if the specified USB drive is plugged in.
- Ignore files that has leading `.` in filename.
- No parameters, no lock, no other complex features - just copy files.

## Requirements

Only Python3 is needed.

## How to use

The simplest way to run is calling `simple-usb-sync` script in this repo folder.

The program will try to read config from these 2 locations, any one of which can work:

- `~/Documents/simple-usb-sync.json`
- `~/.config/simple-usb-sync/config.json`

If neither of these 2 configs exists, the program will leave a config template at `~/Documents/simple-usb-sync.json`. Please open and update the items, including:

- `source`: The folder to sync to USB drive.
- `usbName`: Name of the USB drive showed in file explorer.
- `target`: Folder name in USB drive to store the synced files.

After the config updated, just run the programs. No parameter needed and supported.

## Supported platforms

- macOS

## To do

- Package
- GUI
- Windows support
- Linux support
- Parallel file copy
