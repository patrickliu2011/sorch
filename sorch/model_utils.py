import torch


def get_device_auto():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"

def get_device(device: str):
    if device == "auto":
        return get_device_auto()
    return device