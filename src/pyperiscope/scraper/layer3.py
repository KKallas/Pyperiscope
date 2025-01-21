from pyperiscope import Scope
from .layer2 import Scraper

class Scraper(Scraper):
    def get_scope(self):
        #Check that collector has clic position and area
        if not (self.get_click() or self.get_box()):
            print("Collector must have area and point set before scope can be made")
            return
        #Get offset of the area box
        neg_size_comp = [0,0]
        if self.get_box()[2] < 0:
            neg_size_comp[0] = self.get_box()[2]
        if self.get_box()[3] < 0:
            neg_size_comp[1] = self.get_box()[3]
        area_offset = (self.get_box()[0] - self.get_click()[0] + neg_size_comp[0], 
                       self.get_box()[1] - self.get_click()[1] + neg_size_comp[1])
           
        area_size = (abs(self.get_box()[2]),abs(self.get_box()[3]))
        return Scope(mouse_offset=self.get_click(), area_offset=area_offset, area_size=area_size)