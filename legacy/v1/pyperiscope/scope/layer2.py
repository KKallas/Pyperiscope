from PIL import ImageDraw, ImageFont
from .layer1 import Scope

class Scope(Scope):
    def render_preview(self, base_image=None, marker=None, cropped=True):
        preview = base_image or self.full_image
        if marker:
            area = marker['area']
            mouse_offset = marker['mouse_offset']
            label_text = marker['label']
        else:
            area = self.area_box
            mouse_offset = self.mouse_offset
            label_text = 'set area:'
        preview = preview.copy()
        area = (area[0], area[2], area[1], area[3])
        draw = ImageDraw.Draw(preview, 'RGBA')
        
        draw.rectangle((area[0],area[2],area[1],area[3]), fill=(255, 165, 0, 128), outline=(255, 0, 0), width=2)
        self.draw_label(draw, (area[0],area[2],area[1],area[3]), label_text, self.cursor_size)
        self.draw_mouse_location(draw, mouse_offset, self.cursor_size)
        if cropped:
            return preview.crop(self.crop_box)       
        else:
            return preview
    
    def draw_mouse_location(self, draw, mouse_offset, cursor_size):
        # Draw the location cross
        draw.line(((mouse_offset[0] - cursor_size // 2, mouse_offset[1]),(mouse_offset[0] + cursor_size // 2, mouse_offset[1])), fill=(0, 255, 255), width=2)
        draw.line(((mouse_offset[0], mouse_offset[1] - cursor_size // 2),(mouse_offset[0], mouse_offset[1] + cursor_size // 2)), fill=(0, 255, 255), width=2)
        
    def draw_label(self, draw, area, label_text, cursor_size):
        try:
            font = ImageFont.truetype("arialbd.ttf", cursor_size // 2 - 2)
        except IOError:
            font = ImageFont.load_default()
        
        label_text = label_text.upper()
        label_bbox = draw.textbbox((0, 0), label_text, font=font)
        
        label_position = (area[0] + 5, area[1] + 1)  # 5 pixels offset from the top-left corner
        label_bg = (label_position[0] - 5, label_position[1], label_position[0] + (label_bbox[2] - label_bbox[0]) + 6, label_position[1] + (label_bbox[3] - label_bbox[1]) + 6)
        draw.rectangle(label_bg, fill=(255, 0, 0))  # Red background
        
        # Draw label text
        draw.text(label_position, label_text, fill=(255, 255, 255), font=font) 