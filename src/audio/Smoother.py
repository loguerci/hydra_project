
import numpy as np

class Smoother:
    def __init__(self, alpha=0.5):
        self.alpha = alpha
        self.smoothed_data = None


    def smooth(self, new_data):
        if (self.smoothed_data is None):
            self.smoothed_data = {
                key: value[:] if isinstance(value, np.ndarray) else value
                for key, value in new_data.items()
            }
            return self.smoothed_data
        for key, value in new_data.items():
            if isinstance(value, np.ndarray):  
                self.smoothed_data[key] = (
                    self.alpha * value + (1 - self.alpha) * self.smoothed_data[key]
                )
            elif isinstance(value, (int, np.floating, float)):  
                self.smoothed_data[key] = (
                    self.alpha * value + (1 - self.alpha) * self.smoothed_data[key]
                )
            elif isinstance(value, list) and all(isinstance(v, str) for v in value):  
                self.smoothed_data[key] = value  
            else:
                self.smoothed_data[key] = value  

        return self.smoothed_data