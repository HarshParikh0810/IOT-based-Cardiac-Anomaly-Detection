import numpy as np

def process_ecg_to_restecg(ecg_values):
    if not ecg_values:
        return 0
    signal = np.array(ecg_values)
    mean_val = np.mean(signal)
    std_val = np.std(signal)
    z = (signal - mean_val) / (std_val if std_val != 0 else 1)
    max_dev = np.max(np.abs(z))
    if max_dev < 1.0: return 0
    elif max_dev < 2.0: return 1
    else: return 2
