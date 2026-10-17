from .layer1 import Scraper

class Scraper(Scraper):
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
        
    def get_click(self):
        return tuple(int(n) for n in self.point) if self.point else None
    
    def get_box(self):
        return [int(n) for n in self.box] if self.box else None

    def set_positions(self, click_pos=None, box_dims=None):
        # Update point if provided
        if click_pos is not None:
            self.point = click_pos
            self.dot.set_data([self.point[0]], [self.point[1]])
        
        # Update box if provided
        if box_dims is not None:
            self.box = box_dims
            if not self.box_rect:
                self.box_rect = Rectangle((box_dims[0], box_dims[1]), box_dims[2], box_dims[3],
                                        fill=False, color='red', linewidth=2)
                self.ax.add_patch(self.box_rect)
            else:
                self.box_rect.set_xy((box_dims[0], box_dims[1]))
                self.box_rect.set_width(box_dims[2])
                self.box_rect.set_height(box_dims[3])
            
            # Update corner markers
            for marker in self.corner_markers:
                marker.remove()
            self.corner_markers.clear()
            
            corners = [(box_dims[0], box_dims[1]),
                      (box_dims[0] + box_dims[2], box_dims[1]),
                      (box_dims[0], box_dims[1] + box_dims[3]),
                      (box_dims[0] + box_dims[2], box_dims[1] + box_dims[3])]
            
            for cx, cy in corners:
                marker, = self.ax.plot(cx, cy, 'rs', markersize=8)
                self.corner_markers.append(marker)
        
        self.fig.canvas.draw_idle()
    