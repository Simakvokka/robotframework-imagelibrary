#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from skimage.measure import compare_ssim as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2

from ImageLibrary import utils
from .image_processor import ImageProcessor
from .error_handler import ErrorHandler

class GameWindow(object):

    @utils.add_error_info
    def __init__(self, debug=False):

        self.debug = debug  #TODO: delete?

        self.templates = {}
        self.complex_templates = {}
        self.zones = {}

    ####    IMAGES      ####
    @utils.add_error_info
    def is_image_on_screen(self, image, threshold=0.95, cache=False, zone=None):
        zone = self.zones[zone].get_area() if zone is not None else None
        return ImageProcessor().is_image_on_screen(image, threshold, cache, zone)

    @utils.add_error_info
    def wait_for_image(self, image, threshold=0.95, timeout=15, zone=None):
        zone = self.zones[zone].get_area() if zone is not None else None
        return ImageProcessor().wait_for_image(image, threshold, timeout, zone)

    @utils.add_error_info
    def wait_for_image_to_stop(self, image, timeout=15, threshold=0.95, move_threshold=0.99, step=0.1):
        return ImageProcessor().wait_for_image_to_stop(image, threshold, timeout, move_threshold, step)

    @utils.add_error_info
    def image_should_be_on_screen(self, image, threshold=0.95, cache=False, zone=None):
        zone = self.zones[zone].get_area() if zone is not None else None
        return ImageProcessor().image_should_be_on_screen(image, threshold, cache, zone)


    ####    ANIMATIONS      ####
    @utils.add_error_info
    def wait_for_animation_stops(self, zone=None, timeout=15, threshold=0.9, step=0.1):
        '''Wait until animation stops in the given zone or in the whole active window if zone is not provided.
            Pass _zone_, _timeout_, _step_, _thrreshold_ as arguments. All are optional.

            Examples:
            |   Wait For Animation Stops | zone=zone_coordinates | timeout=15 | threshold=0.95 | step=0.1
        '''
        zone = self.zones[zone].get_area() if zone is not None else None
        return ImageProcessor().wait_for_animation_stops(zone, timeout, threshold, step)

    @utils.add_error_info
    def wait_for_animation_starts(self, zone=None, timeout=15, threshold=0.9, step=0.1):
        '''Same as `Wait For Animation Stops` but on the contrary.
        '''
        zone = self.zones[zone].get_area() if zone is not None else None
        return ImageProcessor().wait_for_animation_starts(zone, timeout, threshold, step)

    @utils.add_error_info
    def is_zone_animating(self, zone=None, threshold=0.9, step=0.1):
        '''Checks if the given zone is animating. Returns boolean.
            Pass _zone_, _threshold_, _step_ as arguments. All are optional. If zone is not provided
                the while active area is taken.

            Examples:
            |   ${is_animating} = | Is Zone Animating | zone=game_zone | threshold=0.9 | step=0.1
        '''
        zone = self.zones[zone].get_area() if zone is not None else None
        return ImageProcessor().is_animating(zone, threshold, step)

    ####    IMAGE RECOGNIZION   ####
    @utils.add_error_info
    def get_number_from_zone(self, zone, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, background=None, contour=False, invert=False, brightness=0, change_mode=True):
        '''Returns the recognized number from the given zone.

            All arguments except _zone_ are optional. _cache_ is False and must not be changed.

            Examples:
            |   ${win} = | Get Number From Zone | zone=win | lang=lang_name | resize_pecent=30 or resize=30 | contrast=1 | background=zone_background | contour=${False} | invert=${False} | brightness=1
        '''
        return self.zones[zone].get_number_from_zone(lang, resize_percent, resize, contrast, cache, background, contour, invert, brightness, change_mode, game)

    @utils.add_error_info
    def get_float_number_from_zone(self, zone, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, contour=False, invert=False, brightness=0, change_mode=True):
        '''Same as `Get Number From Zone` but returns float number.
        '''
        return self.zones[zone].get_float_number_from_zone(lang, resize_percent, resize, contrast, cache, contour, invert, brightness, change_mode)
    
    @utils.add_error_info
    def get_number_with_text_from_zone(self, zone, lang=None, resize_percent=0, resize=0, contrast=0, cache=False, background=None, contour=False, invert=False, brightness=0, change_mode=True):
        '''Same as `Get Number From Zone` but also recognizes text if there are numbers with text in the given zone.
        '''
        return self.zones[zone].get_number_with_text_from_zone(lang, resize_percent, resize, contrast, cache, background, contour, invert, brightness, change_mode, game)
    
    @utils.add_error_info
    def get_text_from_zone(self, zone, lang=None, resize_percent=0, contrast=0, cache=False, contour=False, invert=False, brightness=0):
        '''Returns the recognized text from zone, if there is only text. Arguments logic is the same as for `Get Number From Zone`
        '''
        return self.zones[zone].get_text_from_zone(lang, cache, resize_percent, contrast, contour, invert, brightness)

    @utils.add_error_info
    def get_image_from_zone(self, zone):
        '''Saves the screenshot from the given zone to the launcher 'output' folder as 'scr.png'
        '''
        return self.zones[zone].get_image_from_zone(zone)

    @utils.add_error_info
    def is_template_in_zone(self, template, zone):
        '''Checks if the given template is present in the provided zone, using knn algorythms. Returns boolean.

            Examples:
            |   ${is_on_screen} = | Is Template On Screen | template=templ_name | zone=zone_coordinates
        '''
        return self.zones[zone].is_template_in_zone(template, zone)

    @utils.add_error_info
    def match_template_in_zone(self, template, zone):
        '''Checks if the given template is present in the provided zone. Returns boolean.

            Examples:
            |   ${is_on_screen} = | Match Template On Screen | template=templ_name | zone=zone_coordinates
        '''
        return self.zones[zone].is_template_in_zone(template, zone)

    @utils.add_error_info
    def get_template_position(self, template, zone):
        '''Returns the found template coordinates from the provided zone.

            Examples:
            |   ${pos} = | Get Template Position | template=templ_name | zone=zone_coordinates
        '''
        return self.zones[zone].get_template_position(template, zone)


    ###     COMPARE IMAGES      ###

    def _mse(self, imageA, imageB):
        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;
        # NOTE: the two images must have the same dimension
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])

        # return the MSE, the lower the error, the more "similar"
        # the two images are
        return err


    def _compare(self, imageA, imageB):
        # compute the mean squared error and structural similarity
        # index for the images
        m = self._mse(imageA, imageB)
        s = ssim(imageA, imageB)

        # setup the figure
        fig = plt.figure()
        plt.suptitle("MSE: %.2f, SSIM: %.2f" % (m, s))

        # show first image
        ax = fig.add_subplot(1, 2, 1)
        plt.imshow(imageA, cmap=plt.cm.gray)
        plt.axis("off")

        # show the second image
        ax = fig.add_subplot(1, 2, 2)
        plt.imshow(imageB, cmap=plt.cm.gray)
        plt.axis("off")

        # show the images
        a = float("{0:.2f}".format(s))
        #b = float("{0:.2f}".format(m))
        print(a)
        if a >= 0.65:
            print('success')
            return True
        else:
            print('loose')
            return False

    def compare_images(self, im1, im2):
        '''Compares two given images. Returns boolean.
            Pass the screened image as first, and the template image as second.

            Examples:
            |   Compare Images  | image1 | image2
        '''
        # load the images -- the original, the original + contrast,
        original = cv2.imread(im1)
        contrast = cv2.imread(im2)

        # convert the images to grayscale
        original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        contrast = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)

        # compare the images
        print(self._compare(original, contrast))
        return self._compare(original, contrast)

    ####    OTHER       ####
    #debug only, maybe rework
    @utils.debug_only
    def save_zone_content_to_output(self, zone):
        '''FOR DEBUG: saves the content (screenshot) of the provided zone. Pass zone. Image is saved in the output folder in launcher
        '''
        zone = self.zones[zone].get_area()
        screen_img = ImageProcessor()._get_screenshot(area=zone)
        ErrorHandler().save_pictures([(screen_img, "zone")])