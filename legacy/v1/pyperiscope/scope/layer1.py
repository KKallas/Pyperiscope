import pyautogui
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO

class Scope:
    def __init__(self, saved_dict=None, saved_image=None, mouse_offset=(0, 0), area_offset=(0,0),
                 crop_size=(640, 640), area_size=(64, 64), cursor_size=32, crop_offset=(0,0)):
        self.crop_size = tuple(max(size, 640) for size in crop_size)
        self.area_size = tuple(max(size, 32) for size in area_size)
        self.area_offset = area_offset
        self.mouse_offset = tuple(max(offset, 0) for offset in mouse_offset)
        self.cursor_size = cursor_size
        self.crop_offset = crop_offset
        self.found_locations = []
        
        if saved_dict:
            self.load_from_dict(saved_dict)
            return
        if saved_image:
            self.full_image = saved_image
            self.full_size = saved_image.size
            self.update_crop_and_area()
            return
            
        self.initial_capture()

    def initial_capture(self):
        self.full_image = pyautogui.screenshot()
        self.full_size = self.full_image.size
        self.update_crop_and_area()

    def update_crop_and_area(self, full_image = None):
        full_screen_image = full_image or self.full_image.copy()
        crop_x = min(max((self.mouse_offset[0] + self.crop_offset[0]) - self.crop_size[0] // 2, 0), self.full_size[0] - self.crop_size[0])
        crop_y = min(max((self.mouse_offset[1] + self.crop_offset[1]) - self.crop_size[1] // 2, 0), self.full_size[1] - self.crop_size[1])
        self.crop_box = (crop_x, crop_y, crop_x + self.crop_size[0], crop_y + self.crop_size[1])

        area_x = self.mouse_offset[0] + self.area_offset[0]
        area_y = self.mouse_offset[1] + self.area_offset[1]
        self.area_box = (area_x, area_y, area_x + self.area_size[0], area_y + self.area_size[1])

        self.cropped_image = full_screen_image.copy().crop(self.crop_box)
        
        area_box_clipped = (
            max(0, self.area_box[0]),
            max(0, self.area_box[1]),
            min(self.full_size[0], self.area_box[2]),
            min(self.full_size[1], self.area_box[3])
        )
        
        self.area_image = full_screen_image.copy().crop(area_box_clipped)

    def encode_image(self, image):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def save_dict(self):
        output_dict = {
            'area': self.encode_image(self.area_image),
            'clean_preview': self.encode_image(self.cropped_image),
            'image_metadata': {
                'area_box': self.area_box,
                'area_offset': self.area_offset,
                'area_size': self.area_size, 
                'crop_box': self.crop_box, 
                'crop_size': self.crop_size,
                'cursor_size': self.cursor_size,
                'image_size': self.full_size,
                'mouse_offset': self.mouse_offset
            }}
        return output_dict

    def load_from_dict(self, saved_dict):
        self.area_image = Image.fromarray(np.array(Image.open(BytesIO(base64.b64decode(saved_dict['area'])))), mode="RGB")
        self.cropped_image = Image.fromarray(np.array(Image.open(BytesIO(base64.b64decode(saved_dict['clean_preview'])))), mode="RGB")
        metadata = saved_dict['image_metadata']
        #for attr in ['area_box', 'area_offset', 'area_size', 'crop_box', 'crop_size', 'cursor_size', 'image_size', 'mouse_offset']:
        #    setattr(self, attr, tuple(metadata[attr]))
        self.area_box = metadata['area_box']
        self.area_offset = metadata['area_offset']
        self.area_size = metadata['area_size']
        self.crop_box = metadata['crop_box']
        self.crop_size = metadata['crop_size']
        self.cursor_size = metadata['cursor_size']
        self.full_size = metadata['image_size']
        self.mouse_offset = metadata['mouse_offset']
        # Generate black image in the original desktop size and add only the caprured preview in the right location
        self.full_size = tuple(metadata['image_size'])
        full_image = Image.new('RGB', self.full_size, color='black')
        full_image.paste(self.cropped_image, self.crop_box[:2])
        self.full_image = full_image