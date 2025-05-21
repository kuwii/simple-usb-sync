from setuptools import setup

setup(
    name='simple-usb-sync',
    version='2.0.0',
    description='A simple tool to auto sync files when specific USB drive plugs in',
    author='kuwii',
    url='https://github.com/kuwii/simple-usb-sync',
    license='AGPL-3.0',
    packages=['simple_usb_sync'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'simple-usb-sync=simple_usb_sync.cmd:run_cmd',
            'usbsync=simple_usb_sync.cmd:run_cmd',
            'simple-usb-sync-gui=simple_usb_sync.gui:run_gui',
            'usbsync-gui=simple_usb_sync.gui:run_gui',
        ]
    },
)
