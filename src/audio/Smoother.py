
import numpy as np

class Smoother:
    def __init__(self, alpha=0.5):
        self.alpha = alpha
        self.smoothed_data = None


    def smooth(self, new_data):
        self.make_dict_json_serializable(new_data)
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
    
    def make_dict_json_serializable(self, d):
        for key, value in d.items():
            if isinstance(value, dict):
                self.make_dict_json_serializable(value)
            elif isinstance(value, np.ndarray):
                d[key] = value.tolist()
            elif isinstance(value, np.float32):
                d[key] = float(value)
            elif isinstance(value, list):
                # Conversione ricorsiva per liste contenenti ndarray o float32
                d[key] = [
                    item.tolist() if isinstance(item, np.ndarray) else
                    float(item) if isinstance(item, np.float32) else
                    item for item in value
                ]