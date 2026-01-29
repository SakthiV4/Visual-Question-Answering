import torch
import sys

print(f"Python version: {sys.version}")
try:
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Device: {torch.cuda.get_device_name(0)}")
        print("SUCCESS: GPU is ready!")
    else:
        print("WARNING: CUDA not available")
except ImportError as e:
    print(f"Error importing torch: {e}")
