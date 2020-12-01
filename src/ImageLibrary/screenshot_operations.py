from PIL import Image, ImageChops, ImageOps, ImageEnhance

class ScreenshotOperations:
    """Transform screenshot:
        - changes contours
        - changes contrast: pass float/int values
        - changes brightness: pass float/int values
        - invert image: invert image colors
    """

    def __init__(self):
        pass
    
    def change_contour(self, image):
        result = ImageOps.grayscale(image)
        return result
        
    def change_contrast(self, image, contrast):
        enhancer = ImageEnhance.Contrast(image)
        result = enhancer.enhance(float(contrast))
        return result
    
    def change_brightness(self, image, brightness):
        enhancer = ImageEnhance.Brightness(image)
        result = enhancer.enhance(float(brightness))
        return result

    def invert_image(self, image):
        im = ImageOps.invert(image)
        return im


