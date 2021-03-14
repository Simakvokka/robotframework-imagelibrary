from skimage.metrics import structural_similarity as ssim
import cv2

class ImageComparison(object):
    """Compares two images using a structure similarity algorithm."""
    def __init__(self):
        pass

    ###     COMPARE IMAGES      ###
    def _compare(self, imageA, imageB):
        # compute the structural similarity
        similarity = ssim(imageA, imageB, multichannel=True, gaussian_weights=True)
        print(f'Structural Similarity between images is: {similarity:.2f}')
        if similarity >= 0.98:
            return True
        else:
            return False

    def return_comparison_result(self, im1, im2):
        # load the passed images
        original = cv2.imread(im1)
        contrast = cv2.imread(im2)

        # convert the images to grayscale
        original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        contrast = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)
        return self._compare(original, contrast)