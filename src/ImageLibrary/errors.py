
class CanNotOpenImageException(Exception):
    def __init__(self, image_name):
        self.image_name = image_name

    def __str__(self):
        return f'Image file "{self.image_name}" was not found'

class ImageNotFoundException(Exception):
    def __init__(self, image_name):
        self.image_name = image_name

    def __str__(self):
        return f'Reference image "{self.image_name}" was not found on screen'

class ImageFoundButShouldNotBe(Exception):
    def __init__(self, image_name):
        self.image_name = image_name

    def __str__(self):
        return f'Reference image "{self.image_name}" was found on screen'

class MatrixError(Exception):
    def __init__(self, matrix):
        self.matrix = matrix

    def __str__(self):
        #todo: +1 to all symbols before return
        return f'Something wrong with matrix:\n{str(self.matrix)}'

class ConfigError(Exception):
    def __init__(self, message):
        self.msg = message

    def __str__(self):
        return f'Configuration file corrupted: {self.msg}'

class UnsupportedImageError(Exception):
    def __str__(self):
        return 'Unsupported Image Error'

class UnknownWindowElementError(Exception):
    def __init__(self, element, type, window = None):
        self.element = element
        self.type = type
        self.window = window if window is not None else "main"

    def __str__(self):
        return f'Not found {self.type} {self.element} in {self.window} window'

class WindowNotFoundError(Exception):
    def __init__(self, window):
        self.window = window

    def __str__(self):
        return f'Window {self.window} not found in list of initialized windows'

class CacheError(Exception):
    def __str__(self):
        return 'Cache screenshot is empty. Call Take Cache Screenshot before using cache'

class InitError(Exception):
    def __init__(self, message):
        self.msg = message

    def __str__(self):
        return f'Init ImageLibrary failed: {self.msg}'
