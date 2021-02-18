#tip: SURF AND SIF algorythms are removed from newer opencv releases
#pip install opencv-contrib-python==3.4.2.16 or use CMake built opencv library

import cv2

try:
    from SlotBot import errors, imutils
except ImportError:
    pass    #for stand-alone usage

import numpy as np
import re
import glob
from robot.api import logger as LOGGER

class OpenCV:
    def __init__(self):
        """OpenCV methods to locate templates on screen.
            prepare_image:
                    we need to get an array image to work with. According to the type of passed image this function
                    processes argument and returns a numpy.ndarray
            find_template:
                    operates with arrays and uses cv2 algorythms to search results
            find_multiple_templates:
                    same as find_template for set of passed templates
            prepare_image_to_recognize:
                    used for recognition, processes the given image to grayscale
        """
        try:
            if cv2.ocl.useOpenCL():
                LOGGER.debug("OpenCV module uses OpenCL")
            else:
                LOGGER.debug("OpenCV module doesn't use OpenCL")
        except AttributeError:
            LOGGER.debug("OpenCV module doesn't support OpenCL at all")

    def prepare_image(self, img):
        """S.prepare_image(img) -> np.ndarray
            If img is string, opens corresponding image
            If img is PIL image, converts it to numpy array and change colors to grayscale
        """
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
            for key in sorted(districts.keys()):
                if points_in_the_same_district(pt, key, width, height):
                    districts[key].append(pt)
                    break
            else:
                districts[pt] = [pt]

        #2 sort every district by threshold
        #3 point with max thershold wins
        result = []
        for district in sorted(districts.values()):
            sorted_district = sorted(district, key=lambda tup: tup[4], reverse=True)
            result.append(sorted_district[0])

        #4 ???

        #5 PROFIT
        return result

    def find_template(self, what, where, threshold=0.99):
        """S.find_template_pos_and_thershold(what, where) -> pos, thershold"""
        screen = self.prepare_image(where)
        tmpl = self.prepare_image(what)
        threshold = float(threshold)

        try:
            res = cv2.matchTemplate(screen, tmpl, cv2.TM_CCOEFF_NORMED)
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res)

            height, width = tmpl.shape
            if maxVal >= threshold:
                return (maxLoc[0], maxLoc[1], width, height, maxVal)
            else:
                return None
        except:
            return None

    def find_multiple_templates(self, what, where, threshold=0.99):
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
        """S.prepare_image_to_recognize(img) -> PIL image"""
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
        #load the image, convert it to grayscale, and detect edges
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
        """Uses the K-Nearest Neighbours algorithm to find the match on screen.
        """

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
        im.save('objects_match_knn_result.png')

        if len(good_matches) > 0:
            return True
        else:
            return False

class ImageToMatrix(object):
    """Locates images from passed set of templates (in our case symbols images with all kinds of effects and animations)
        and returns symbols matrix in numeric array."""

    def __init__(self):
        pass

    def analyze_dataset(self, x, y, path_to_templates, image_to_analyze, threshold):

        #makes a list of all template images from passed directory
        templates = glob.glob(path_to_templates)
        #reads the image from screenshot and convert it into Grey Color
        img_rgb = cv2.imread(image_to_analyze)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        #gets width and height for the screenshot image
        q_w, q_h = img_gray.shape[::-1]

        #tries to find symbol template matching on the screenshot image and returns as list with matching coordinates
        collection = []
        for myfile in templates:
            template = cv2.imread(myfile, 0)

            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            #threshold = int(threshold)
            loc = np.where(res >= threshold)
            matches = myfile, zip(*loc[::-1])
            #transforms 1.9.png, 2.3.png into 1 and 2. etc to get the normal symbol id
            pattern = matches[0]
            match = re.search("[0-9]+.[0-9]+.png", pattern)
            symbol = match.group(0)
            symbol = re.sub('.[0-9]+.png', '', str(symbol))

            m = (symbol, matches[1])

            collection.append(m)

        return self.image_to_matrix(x, y, q_w, q_h, collection)

    def image_to_matrix(self, x,
                              y,
                              width,
                              height,
                              found_data):

        """Transforms found symbols on the screenshot into matrix view. Returns an array."""

        result_arr = np.zeros((y, x), dtype=int)
        col_step = int(width / x)
        row_step = int(height / y)

        for el in found_data:
            symbol = el[0]
            for coordinate in el[1]:
                row = round(coordinate[1] / float(row_step))
                col = round(coordinate[0] / float(col_step))
                result_arr[int(row), int(col)] = symbol

        return result_arr


import unittest
from PIL import Image
import os

# class OpenCVTests(unittest.TestCase):
#     def setUp(self):
#         self.test_data = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data", "open_cv")
#         self.cv = OpenCV()
#         self.compare_folder = os.path.join(self.test_data, "compare")
#
#     def tearDown(self):
#         self.test_data = None
#         self.cv = None
#
#     def test_find_template(self):
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "template.png"),
#             os.path.join(self.test_data, "screen.png")))
#
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "gamble_black.png"),
#             os.path.join(self.test_data, "gamble_screen.png")))
#
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "gd_logo.png"),
#             os.path.join(self.test_data, "gd_screen.png")))
#
#     def test_find_template_noise(self):
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "template.png"),
#             os.path.join(self.test_data, "noise.png")))
#         self.assertFalse(self.cv.find_template(
#             os.path.join(self.test_data, "template.png"),
#             os.path.join(self.test_data, "noise.png"),
#             threshold = 1))
#
#     def test_find_template_negative(self):
#         self.assertFalse(self.cv.find_template(
#             os.path.join(self.test_data, "template.png"),
#             os.path.join(self.test_data, "neg.png")))
#
#         self.assertFalse(self.cv.find_template(
#             os.path.join(self.test_data, "win.png"),
#             os.path.join(self.test_data, "screen2.png")))
#
#     def test_find_template_at_image(self):
#         """call find_template with image instead of path"""
#         img = Image.open(os.path.join(self.test_data, "screen.png"))
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "template.png"), img))
#
#         screen = Image.open(os.path.join(self.test_data, "gd_screen.png"))
#         logo = Image.open(os.path.join(self.test_data, "gd_logo.png"))
#         self.assertTrue(self.cv.find_template(logo, screen))
#
#         #images are slightly different by background
#         big_win = Image.open(os.path.join(self.test_data, "big_win.png"))
#         win = Image.open(os.path.join(self.test_data, "win.png"))
#         self.assertTrue(self.cv.find_template(win, big_win))
#
#         fw = Image.open(os.path.join(self.test_data, "firework.png"))
#         screen = Image.open(os.path.join(self.test_data, "gd_screen_fw.png"))
#         self.assertTrue(self.cv.find_template(fw, screen, 0.65))
#
#     def test_find_symbols(self):
#         img = Image.open(os.path.join(self.test_data, "screen3.png"))
#         threshold = 0.7
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "symbols", "00.png"), img, threshold))
#         self.assertFalse(self.cv.find_template(
#             os.path.join(self.test_data, "symbols", "01.png"), img, threshold))
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "symbols", "02.png"), img, threshold))
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "symbols", "03.png"), img, threshold))
#         self.assertFalse(self.cv.find_template(
#             os.path.join(self.test_data, "symbols", "04.png"), img, threshold))
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "symbols", "05.png"), img, threshold))
#         self.assertFalse(self.cv.find_template(
#             os.path.join(self.test_data, "symbols", "06.png"), img, threshold))
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "symbols", "07.png"), img, threshold))
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "symbols", "08.png"), img, threshold))
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "symbols", "09.png"), img, threshold))
#         self.assertFalse(self.cv.find_template(
#             os.path.join(self.test_data, "symbols", "10.png"), img, threshold))
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "symbols", "11.png"), img, threshold))
#         self.assertTrue(self.cv.find_template(
#             os.path.join(self.test_data, "symbols", "12.png"), img, threshold))
#
#     def test_8_bit_image(self):
#         screen = Image.open(os.path.join(self.test_data, "50d_screen.png"))
#         help = Image.open(os.path.join(self.test_data, "50d_help.png"))
#         self.assertEqual(help.mode, 'P')
#         self.assertTrue(self.cv.find_template(help, screen))
#
#     #def test_compare_images_identical(self):
#     #    img1 = Image.open(os.path.join(self.compare_folder, "3.png"))
#     #    img2 = Image.open(os.path.join(self.compare_folder, "3_2.png"))
#     #    self.assertAlmostEqual(self.cv.get_images_difference(img1, img2), 1)
#     #
#     #def test_compare_images_similar(self):
#     #    img1 = Image.open(os.path.join(self.compare_folder, "3.png"))
#     #    img2 = Image.open(os.path.join(self.compare_folder, "4.png"))
#     #    self.assertGreater(self.cv.get_images_difference(img1, img2), 0.9)
#     #
#     #def test_compare_images_different(self):
#     #    img1 = Image.open(os.path.join(self.compare_folder, "1.png"))
#     #    img2 = Image.open(os.path.join(self.compare_folder, "2.png"))
#     #    self.assertLess(self.cv.get_images_difference(img1, img2), 0.75)
#     #
#     #    img1 = Image.open(os.path.join(self.compare_folder, "black.png"))
#     #    img2 = Image.open(os.path.join(self.compare_folder, "white.png"))
#     #    self.assertLess(self.cv.get_images_difference(img1, img2), 0.1)
#
#     #def test_images_equal(self):
#     #    img1 = Image.open(os.path.join(self.compare_folder, "3.png"))
#     #    img2 = Image.open(os.path.join(self.compare_folder, "3_2.png"))
#     #    img3 = Image.open(os.path.join(self.compare_folder, "4.png"))
#     #
#     #    self.assertTrue(self.cv.are_images_equal(img1, img2, 0.99))
#     #    self.assertFalse(self.cv.are_images_equal(img1, img3, 0.99))
#     #    self.assertTrue(self.cv.are_images_equal(img1, img3, 0.9))
#     #
#     #def test_images_different(self):
#     #    img1 = Image.open(os.path.join(self.compare_folder, "1.png"))
#     #    img2 = Image.open(os.path.join(self.compare_folder, "2.png"))
#     #    img3 = Image.open(os.path.join(self.compare_folder, "3.png"))
#     #    black = Image.open(os.path.join(self.compare_folder, "black.png"))
#     #    white = Image.open(os.path.join(self.compare_folder, "white.png"))
#     #
#     #    self.assertFalse(self.cv.are_images_equal(img1, img2, 0.9))
#     #    self.assertFalse(self.cv.are_images_equal(img2, img3, 0.9))
#     #    self.assertFalse(self.cv.are_images_equal(black, white, 0.01))
#
#     def test_check_buttons(self):
#         disabled = Image.open(os.path.join(self.test_data, "start_disabled.png"))
#         enabled = Image.open(os.path.join(self.test_data, "start.png"))
#         highlighted = Image.open(os.path.join(self.test_data, "start_highlighted.png"))
#
#         self.assertFalse(self.cv.find_template(disabled, enabled, 0.75))
#         self.assertFalse(self.cv.find_template(disabled, highlighted, 0.75))
#         self.assertTrue(self.cv.find_template(enabled, highlighted, 0.75))
#
#     #this test is using for debug reasons - when smth wrong with screenshot recognision
# #    def test_check_wtf_wrong_with_my_template(self):
# #        screen = Image.open(os.path.join(self.test_data, "1-screen.png"))
# #        tmpl = Image.open(os.path.join(self.test_data, "1-template.png"))
# #        self.assertTrue(self.cv.find_template(tmpl, screen))

from optparse import OptionParser
import os
try:
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
except ImportError:
    pass

def draw_poses(image, pos):
    for p in pos:
        top_left = tuple(p[0:2])
        bottom_right = (p[0] + p[2], p[1] + p[3])
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_COMPLEX
        thr = p[4] - (p[4] % 0.001)
        pos_y = p[1]-5
        if pos_y < 25:
            pos_y = p[1]+p[3]+25
        cv2.putText(image, '{0:.3f}'.format(thr), (p[0], pos_y), font, 1, (0, 255, 0), 1, cv2.LINE_AA)

    return image

def show_image(image):
    plt.axis("off")
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.show()

if __name__ == '__main__':
    parser = OptionParser("usage: %prog [options] what where")
    parser.add_option("-m", "--multiple", action="store_true", dest="multiple",
                help="find multiple templates", default=False)
    parser.add_option("-t", "--threshold", action="store", dest="threshold",
                help="Minimum threshold. It is mandatory when multiple templates are searching", default=0)
    parser.add_option("--test", action="store_true", dest="run_tests",
                help="run unittests", default=False)

    (options, args) = parser.parse_args()
    if options.run_tests:
        pass
        #todo
        #unittest.main()
    else:
        cv = OpenCV()
        if len(args) != 2:
            parser.error("Please, set template and screen images")

        what, where = args
        #what = os.path.join(os.getcwd(), what)
        #where = os.path.join(os.getcwd(), where)
        if options.multiple:
            pos = cv.find_multiple_templates(what, where, options.threshold)
            if len(pos) == 0:
                print("Nothing found!")
            else:
                img = draw_poses(cv2.imread(where), pos)
                show_image(img)
        else:
            pos = cv.find_template(what, where, options.threshold)
            if pos is None:
                print("Nothing found!")
            else:
                print("threshold: {:.3f}".format(pos[4] - (pos[4] % 0.001)))
                img = draw_poses(cv2.imread(where), [pos])
                show_image(img)

