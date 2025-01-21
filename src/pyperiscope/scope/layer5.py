from .layer4 import Scope

class Scope(Scope):
    def generate_scope_string(self, step=None):
        
        if step==None:
            step=self
        
        defaults = {'mouse_offset': (0, 0), 'area_offset': (0, 0), 'area_size': (64, 64), 'crop_size': (640, 640), 'cursor_size': 32}
        current_values = {'mouse_offset': step.mouse_offset, 'area_offset': step.area_offset, 'area_size': step.area_size, 'crop_size': step.crop_size, 'cursor_size': step.cursor_size}
        
        # Filter out values that match defaults
        non_default = {
            key: value for key, value in current_values.items()
            if value != defaults[key]
        }
        
        if not non_default:
            return "step = Scope()"
        
        # Format non-default values
        params = []
        for key, value in non_default.items():
            if isinstance(value, tuple):
                formatted_value = str(value)
            else:
                formatted_value = str(value)
            params.append(f"{key}={formatted_value}")
        
        return f"step = Scope({', '.join(params)})"