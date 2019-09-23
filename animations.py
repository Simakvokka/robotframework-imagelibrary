from __future__ import absolute_import


from ImageLibrary.image_processor import ImageProcessor
from ImageLibrary import utils


class Animations(object):

    def __init__(self, error_handler, output_dir):
        self.error_handler = error_handler
        self.output_dir = output_dir
        
        
        
    ####    ANIMATIONS      ####
    @utils.add_error_info
    def wait_for_animation_stops(self, zone=None, timeout=15, threshold=0.9, step=0.1):
        '''Wait until animation stops in the given zone or in the whole active window if zone is not provided.
            Pass _zone_, _timeout_, _step_, _thrreshold_ as arguments. All are optional.
            Default values are given in the example.

            Examples:
            |   Wait For Animation Stops | zone=zone_coordinates | timeout=15 | threshold=0.95 | step=0.1
        '''

        return ImageProcessor(self.error_handler, self.output_dir).wait_for_animation_stops(zone, timeout, threshold, step)


    @utils.add_error_info
    def wait_for_animation_starts(self, zone=None, timeout=15, threshold=0.9, step=0.1):
        '''Same as `Wait For Animation Stops` but on the contrary.
           Pass _zone_, _timeout_, _step_, _thrreshold_ as arguments. All are optional.
           Default values are given in the example.

            Examples:
            |   Wait For Animation Starts | zone=zone_coordinates | timeout=15 | threshold=0.95 | step=0.1
        '''

        return ImageProcessor(self.error_handler, self.output_dir).wait_for_animation_starts(zone, timeout, threshold, step)


    @utils.add_error_info
    def is_zone_animating(self, zone=None, threshold=0.9, step=0.1):
        '''Checks if the given zone is animating. Returns boolean.
            Pass _zone_, _threshold_, _step_ as arguments. All are optional. If zone is not provided
                the whole active area is taken.
            Default values are given in the example.

            Examples:
            |   ${is_animating} = | Is Zone Animating | zone=game_zone | threshold=0.9 | step=0.1
        '''

        return ImageProcessor(self.error_handler, self.output_dir).is_animating(zone, threshold, step)
