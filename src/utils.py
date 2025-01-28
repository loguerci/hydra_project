import numpy as np

def make_dict_json_serializable(d):
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