from .layer1 import Binoculars
from PIL import Image
import markdown

class Binoculars(Binoculars):
    def __init__(self, width=400):
        super().__init__(width)
        self.update_both(self.error_image, self.error_image)
        self.set_description("# No step loaded")
        
    def update_both(self, image1, image2):
        """Update both images at once"""
        if not isinstance(image1, Image.Image) or not isinstance(image1, Image.Image):
            raise TypeError("Inputs must be a PIL Image")

        image1_bytes = self._convert_to_bytes(image1)
        image2_bytes = self._convert_to_bytes(image2)
        self.widget1.value = image1_bytes
        self.widget2.value = image2_bytes
    
    def set_description(self, text):
        """Update description text with markdown formatting"""
        # Convert markdown to HTML
        if not text == None:
            md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])
            self.description.value = md.convert(text)
    
    def set_error(self, text):
        """Update error text with markdown formatting"""
        # Convert markdown to HTML with red color for errors
        if not text == None:
            md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])
            self.error_text.value = md.convert(text)