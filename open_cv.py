#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import cv2
from ImageLibrary import imutils
from PIL import Image

try:
    from SlotBot import errors
except ImportError:
    pass    #for stand-alone usage

import numpy as np
from robot.api import logger as LOGGER

class OpenCV(object):

    def __init__(self):

        try:
            if cv2.ocl.useOpenCL():
                LOGGER.info("OpenCV module uses OpenCL")
            else:
                LOGGER.info("OpenCV module doesn't use OpenCL")
        except AttributeError:
            LOGGER.info("OpenCV module doesn't support OpenCL at all")

    def prepare_image(self, img):
        '''S.prepare_image(img) -> np.ndarray
            If img is string, opens corresponding image
            If img is PIL image, converts it to numpy array and change colors to grayscale
        '''
        prepared = None
        if isinstance(img, str):
            prepared = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        elif isinstance(img, Image.Image):
            #convert 8-bit image to 32-bit
            if img.mode == 'P':     #colored 8bit
                prepared = np.array(img.convert('RGBA'))
            elif img.mode == 'RGBA' or img.mode == 'RGB':   #colored 24-bit
                prepared = np.array(img)
            elif img.mode == 'L':    #grayscaled 8bit
                prepared = np.array(img.convert('RGBA'))
            else:
                raise errors.UnsupportedImageError

            prepared = cv2.cvtColor(prepared, cv2.COLOR_RGB2GRAY)
        elif isinstance(img, np.ndarray):
            if len(img.shape) == 3:
                prepared = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            else:
                prepared = img

        if prepared is None:
            raise ValueError('OpenCV.prepare_image: error when open image {}'.format(img))

        return prepared

    def _remove_noise(self, array, width, height):
        def points_in_the_same_district(pt1, pt2, width, height):
            return abs(pt1[0] - pt2[0]) < width and abs(pt1[1] - pt2[1]) < height

        #1 find points for every district
        districts = {}
        for pt in array:
            for key in districts.iterkeys():
                if points_in_the_same_district(pt, key, width, height):
                    districts[key].append(pt)
                    break
            else:
                districts[pt] = [pt]

        #2 sort every district by threshold
        #3 point with max thershold wins
        result = []
        for district in districts.itervalues():
            sorted_district = sorted(district, key=lambda tup: tup[4], reverse=True)
            result.append(sorted_district[0])

        #4 ???

        #5 PROFIT
        return result

    def find_template(self, what, where, threshold=0.75):
        '''S.find_template_pos_and_thershold(what, where) -> pos, thershold'''
        screen = self.prepare_image(where)
        tmpl = self.prepare_image(what)
        threshold = float(threshold)

        res = cv2.matchTemplate(screen, tmpl, cv2.TM_CCOEFF_NORMED)

        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res)

        height, width = tmpl.shape

        if maxVal >= threshold:
            return (maxLoc[0], maxLoc[1], width, height, maxVal)
        else:
            return None

    def find_multiple_templates(self, what, where, threshold=0.75):
        screen = self.prepare_image(where)
        tmpl = self.prepare_image(what)
        threshold = float(threshold)

        res = cv2.matchTemplate\
            (screen, tmpl, cv2.TM_CCOEFF_NORMED)

        loc = np.where(res >= threshold)
        pos = []
        height, width = tmpl.shape
        for pt in zip(*loc[::-1]):
            pos.append((pt[0], pt[1], width, height, res[pt[1], pt[0]])) 

        pos = self._remove_noise(pos, width, height)

        return pos

    def prepare_image_to_recognize(self, img):
        '''S.prepare_image_to_recognize(img) -> PIL image'''
        if img.mode == 'P':
            prep = np.array(img.convert('RGBA'))
        else:
            prep = np.array(img)

        prep = cv2.cvtColor(prep, cv2.COLOR_RGB2GRAY)
        prep -= prep.min()
        max = prep.max()
        for i in range(prep.shape[0]):
            for j in range(prep.shape[1]):
                prep[i][j] = np.uint8(prep[i][j]*255.0/max)
        #ret, thresh = cv2.threshold(prep, prep.min() + (prep.max() - prep.min())/2, 255, cv2.THRESH_TRUNC)
        return Image.fromarray(prep).convert('RGB')

class MatchObjects(object):
    def __init__(self):
        self.found = None

    def match_objects(self, img, screen, threshold=0.98):
        #load the image image, convert it to grayscale, and detect edges
        template = cv2.imread(img)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template = cv2.Canny(template, 50, 200)
        (tH, tW) = template.shape[:2]
        cv2.imwrite('templ.png', template)

        #convert PIL Image into cv2 format:
        image = np.asarray(screen)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        for scale in np.linspace(0.2, 1.0, 20)[::-1]:

            resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])

            if resized.shape[0] < tH or resized.shape[1] < tW:
                break

            edged = cv2.Canny(resized, 50, 200)
            #result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
            result = cv2.matchTemplate(edged, template, cv2.TM_CCORR_NORMED)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            if maxVal >= threshold:
                clone = np.dstack([edged, edged, edged])
                cv2.rectangle(clone, (maxLoc[0], maxLoc[1]), (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
                cv2.imwrite('screen.png', clone)

                return True
            else:
                LOGGER.error('No matching template found.')
            return False

    #use it when prepairing yaml file
    def match_and_return_coordinates(self, img, screen, threshold=0.98):
        #load the image image, convert it to grayscale, and detect edges
        template = cv2.imread(img)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template = cv2.Canny(template, 50, 200)
        (tH, tW) = template.shape[:2]
        #cv2.imwrite('templ.png', template)

        #convert PIL Image into cv2 format:
        image = np.asarray(screen)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        for scale in np.linspace(0.2, 1.0, 20)[::-1]:

            resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])

            if resized.shape[0] < tH or resized.shape[1] < tW:
                break

            edged = cv2.Canny(resized, 50, 200)
            #result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
            result = cv2.matchTemplate(edged, template, cv2.TM_CCORR_NORMED)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            if maxVal >= threshold:
                clone = np.dstack([edged, edged, edged])
                cv2.rectangle(clone, (maxLoc[0], maxLoc[1]), (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
                #cv2.imwrite('screen.png', clone)
                position = (maxLoc[0], maxLoc[1]), (tW, tH)

                coordinates = []

                for i in position:
                    for j in i:
                        coordinates.append(j)

                return coordinates
            else:
                LOGGER.error('No matching template found.')

    def match_objects_with_knn(self, screen, template, ratio_threshold=0.5):

        img1 = cv2.imread(template, 2)  # what
        img1 = cv2.Canny(img1, 100, 700, apertureSize=3, L2gradient=False)
        img2 = np.asarray(screen)  # where
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        img2 = cv2.Canny(img2, 100, 700, apertureSize=3, L2gradient=False)

        # -- Step 1: Detect the keypoints using SURF Detector, compute the descriptors
        minHessian = 400
        detector = cv2.xfeatures2d.SURF_create(hessianThreshold=minHessian)
        keypoints1, descriptors1 = detector.detectAndCompute(img1, None)
        keypoints2, descriptors2 = detector.detectAndCompute(img2, None)
        # -- Step 2: Matching descriptor vectors with a FLANN based matcher
        # Since SURF is a floating-point descriptor NORM_L2 is used
        matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_FLANNBASED)
        knn_matches = matcher.knnMatch(descriptors1, descriptors2, 2)
        # -- Filter matches using the Lowe's ratio test
        ratio_thresh = ratio_threshold
        good_matches = []
        for m, n in knn_matches:
            if m.distance < ratio_thresh * n.distance:
                good_matches.append(m)

        # -- Draw matches
        img_matches = np.empty((max(img1.shape[0], img2.shape[0]), img1.shape[1] + img2.shape[1], 3), dtype=np.uint8)
        cv2.drawMatches(img1, keypoints1, img2, keypoints2, good_matches, img_matches,
                        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        # -- Save matched result
        im = Image.fromarray(img_matches)
        im.save('objects_match_result.png')

        if len(good_matches) > 0:
            return True
        else:
            return False