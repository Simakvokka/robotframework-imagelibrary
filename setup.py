import re
from os.path import abspath, dirname, join
from setuptools import setup, find_packages


CURDIR = dirname(abspath(__file__))

with open(join(CURDIR, 'src', 'ImageLibrary', '__init__.py')) as f:
    VERSION = re.search("\n__version__ = '(.*)'", f.read()).group(1)
with open(join(CURDIR, 'README.md')) as f:
    DESCRIPTION = f.read()

setup(
    name             = 'robotframework-imagelibrary',
    version          = '0.2.0',
    description      = 'Image Processing Library For Robot Framework',
    long_description = DESCRIPTION,
    author           = 'Prokhorova Maria',
    author_email     = 'msklenaj@gmail.com',
    long_description_content_type="text/markdown",
    url              = 'https://github.com/Simakvokka/robotframework-imagelibrary',
    license          = 'Apache License 2.0',
    keywords         = 'robotframework testing testautomation image processing',
    platforms        = 'Windows',
    python_requires  = '>=2.7.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    install_requires = ['robotframework', 'opencv-python', 'pyautogui', 'numpy', 'pytesseract', 'scikit-image', 'pillow', 'future'],
    package_dir      = {'': 'src'},
    packages         = find_packages('src')
)