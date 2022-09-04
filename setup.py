from setuptools import setup

setup(
    name='simple-usb-sync',
    version='0.1.0',
    description='A simple tool to auto sync files when specific USB drive plugs in',
    author='kuwii',
    url='https://github.com/kuwii/simple-usb-sync',
    license='AGPL-3.0',
    packages=['simple_usb_sync'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'simple-usb-sync=simple_usb_sync.main:main',
            'usbsync=simple_usb_sync.main:main',
        ]
    },
)
