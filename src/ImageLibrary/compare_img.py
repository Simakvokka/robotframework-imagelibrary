# import the necessary packages
from skimage.measure import compare_ssim as ssim
import numpy as np
import cv2

class ImageComparison(object):
    def __init__(self):
        pass


    def mse(self, imageA, imageB):
        """
        The 'Mean Squared Error' between the two images is the
        sum of the squared difference between the two images;
        NOTE: the two images must have the same dimension
        """
        
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])

        # return the MSE, the lower the error, the more "similar" the two images are
        return err


    def compare(self, imageA, imageB, title):
        """Computes the mean squared error and structural similarity
        index for the images"""
        
        m = self.mse(imageA, imageB)
        s = ssim(imageA, imageB)

        a = float("{0:.2f}".format(s))
        b = float("{0:.2f}".format(m))

        if a < 0.65 or a == 1:
            return True
        else:
            print('Images are unequal')
            return False

    def return_comparison_result(self, origin, contrast):
        # load the images -- the original, the original + contrast,
        original = cv2.imread(origin)
        contrast = cv2.imread(contrast)

        # convert the images to grayscale
        original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        contrast = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)

        # compare the images
        return self.compare(original, contrast, "Original vs. Contrast")