from ipywidgets import widgets
from IPython.display import display as ipython_display
from pyperiscope import Scope
from PIL import Image, ImageDraw, ImageFont
import io
import dill
import pyautogui
import time
import pyperclip

class Binoculars:
    def __init__(self, width=400):
        self.width = width
        self.image1 = None
        self.image2 = None
        self.box = None
        self.image = None
        self.error_image = self._create_error_image(320,320)
        self._create_widgets()

    def _create_error_image(self, width, height):
        # Create black background image
        img = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(img)
        
        # Draw gray cross
        gray = (128, 128, 128)
        cross_width = max(2, min(width, height) // 100)  # Dynamic line width
        # Horizontal line
        draw.line((0, height//2, width, height//2), fill=gray, width=cross_width)
        # Vertical line
        draw.line((width//2, 0, width//2, height), fill=gray, width=cross_width)
        
        # Add text
        text = "Image could not be loaded"
        try:
            # Try to load a common font
            font = ImageFont.truetype("arial.ttf", size=min(width, height)//15)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Calculate text position
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw white text with black border for better visibility
        draw.text((x, y), text, fill='white', font=font, stroke_width=2, stroke_fill='black')
        
        return img   

    def _create_widgets(self):
        """Initialize all widgets including text areas"""
        # Create description text widget (Markdown)
        self.description = widgets.HTML(
            value='',
            placeholder='Description',
            description='',
        )
        
        # Create image widgets
        self.widget1 = widgets.Image(format='png', width=self.width)
        self.widget2 = widgets.Image(format='png', width=self.width)
        self.image_box = widgets.VBox([self.widget1, self.widget2])
        
        # Create error text widget (Markdown)
        self.error_text = widgets.HTML(
            value='',
            placeholder='Error messages',
            description='',
        )
        
        # Stack all widgets vertically
        self.box = widgets.VBox([
            self.description,
            self.image_box,
            self.error_text
        ])
        
        ipython_display(self.box)

    def _convert_to_bytes(self, pil_image):
        """Convert PIL image to bytes"""
        buf = io.BytesIO()
        pil_image.save(buf, format='PNG')
        return buf.getvalue()