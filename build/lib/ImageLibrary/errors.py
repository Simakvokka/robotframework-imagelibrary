# -*- coding: utf-8 -*-

class CanNotOpenImageException(Exception):
    def __init__(self, image_name):
        self.image_name = image_name

    def __str__(self):
        return 'Image file "%s" was not found' % self.image_name

class ImageNotFoundException(Exception):
    def __init__(self, image_name):
        self.image_name = image_name

    def __str__(self):
        return 'Reference image "%s" was not found on screen' % self.image_name

class ImageFoundButShouldNotBe(Exception):
    def __init__(self, image_name):
        self.image_name = image_name

    def __str__(self):
        return 'Reference image "%s" was found on screen' % self.image_name

class MatrixError(Exception):
    def __init__(self, matrix):
        self.matrix = matrix

    def __str__(self):
        #todo: +1 to all symbols before return
        return 'Something wrong with matrix:\n%s' % str(self.matrix)

class ConfigError(Exception):
    def __init__(self, message):
        self.msg = message

    def __str__(self):
        return 'Configuration file corrupted: %s' % self.msg

class UnsupportedImageError(Exception):
    def __str__(self):
        return 'Unsupported Image Error'

class UnknownWindowElementError(Exception):
    def __init__(self, element, type, window = None):
        self.element = element
        self.type = type
        self.window = window if window is not None else "main"

    def __str__(self):
        return 'Not found %s %s in %s window' % (self.type, self.element, self.window)

class WindowNotFoundError(Exception):
    def __init__(self, window):
        self.window = window

    def __str__(self):
        return 'Window %s not found in list of initiaized windows' % self.window

class CacheError(Exception):
    def __str__(self):
        return 'Cache screenshot is empty. Call Take Cache Screenshot before using cache'

class InitError(Exception):
    def __init__(self, message):
        self.msg = message

    def __str__(self):
        return 'Init SlotBot failed: %s' % self.msg
