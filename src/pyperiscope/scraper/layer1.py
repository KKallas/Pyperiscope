import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.patches import Rectangle
import matplotlib
matplotlib.use('widget')

class Scraper:
    def __init__(self, pil_image: Image.Image):
        # Single point and box storage
        self.point = None
        self.box = None
        self.start_point = None
        
        # Setup display
        img_array = np.array(pil_image)
        self.fig, self.ax = plt.subplots(figsize=(10,10))
        self.fig.tight_layout(pad=0)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        # Show image and initialize point marker
        self.ax.imshow(img_array, extent=(0, img_array.shape[1], img_array.shape[0], 0))
        self.dot, = self.ax.plot([], [], 'ro')
        self.box_rect = None
        self.corner_markers = []
        
        def draw_corners(x, y, w, h):
            # Clear old markers
            for marker in self.corner_markers:
                marker.remove()
            self.corner_markers.clear()
            
            # Draw new corner markers
            corners = [(x,y), (x+w,y), (x,y+h), (x+w,y+h)]
            for cx, cy in corners:
                marker, = self.ax.plot(cx, cy, 'rs', markersize=8)
                self.corner_markers.append(marker)
        
        def on_press(event):
            if event.inaxes and event.button == 1 and self.fig.canvas.toolbar.mode == '':
                self.start_point = (event.xdata, event.ydata)
                # Start drawing new box
                if self.box_rect:
                    self.box_rect.set_width(0)
                    self.box_rect.set_height(0)
                else:
                    self.box_rect = Rectangle(self.start_point, 0, 0, fill=False, 
                                           color='red', linewidth=2)
                    self.ax.add_patch(self.box_rect)
        
        def on_motion(event):
            if event.inaxes and self.start_point and self.fig.canvas.toolbar.mode == '':
                width = event.xdata - self.start_point[0]
                height = event.ydata - self.start_point[1]
                # Update box size while dragging
                self.box_rect.set_xy(self.start_point)
                self.box_rect.set_width(width)
                self.box_rect.set_height(height)
                draw_corners(self.start_point[0], self.start_point[1], width, height)
                self.fig.canvas.draw_idle()
        
        def on_release(event):
            if event.inaxes and event.button == 1 and self.start_point and self.fig.canvas.toolbar.mode == '':
                # Check if it's a click (small movement) or box (drag)
                if abs(event.xdata - self.start_point[0]) < 3 and abs(event.ydata - self.start_point[1]) < 3:
                    # Update point only
                    self.point = self.start_point
                    self.dot.set_data([self.point[0]], [self.point[1]])
                    # Restore box if it exists
                    if self.box:
                        self.box_rect.set_xy((self.box[0], self.box[1]))
                        self.box_rect.set_width(self.box[2])
                        self.box_rect.set_height(self.box[3])
                else:
                    # Update box
                    self.box = (self.start_point[0], self.start_point[1],
                              event.xdata - self.start_point[0],
                              event.ydata - self.start_point[1])
                    draw_corners(*self.box)
                
                self.start_point = None
                self.fig.canvas.draw_idle()
        
        # Connect events
        self.fig.canvas.mpl_connect('button_press_event', on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', on_motion)
        self.fig.canvas.mpl_connect('button_release_event', on_release)
        plt.show()
    
    def clear_all(self):
        self.point = None
        self.box = None
        self.dot.set_data([], [])
        if self.box_rect:
            self.box_rect.set_width(0)
            self.box_rect.set_height(0)
        for marker in self.corner_markers:
            marker.remove()
        self.corner_markers.clear()
        self.fig.canvas.draw_idle()