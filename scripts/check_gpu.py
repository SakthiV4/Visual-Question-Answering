"""
Check GPU availability
"""
import torch

print("=" * 60)
print("GPU Check")
print("=" * 60)
print()

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"Number of GPUs: {torch.cuda.device_count()}")
    print(f"Current GPU: {torch.cuda.current_device()}")
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print()
    print("[SUCCESS] GPU is available and ready to use!")
else:
    print()
    print("[WARNING] No GPU detected!")
    print()
    print("Possible reasons:")
    print("1. No NVIDIA GPU installed")
    print("2. CUDA drivers not installed")
    print("3. PyTorch installed without CUDA support")
    print()
    print("To check PyTorch CUDA support:")
    print("  pip show torch")
    print()
    print("To install PyTorch with CUDA:")
    print("  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
