# Quick Start Guide - VQA Training

## ⚡ 5-Minute Quick Start

### Prerequisites

- Python 3.8+
- CUDA-capable GPU (recommended)
- 20GB free disk space
- VSCode with Jupyter extension

### Steps

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Download Data** (Choose one method)

Method A - Hugging Face (Easiest):

```python
from datasets import load_dataset
dataset = load_dataset('HuggingFaceM4/VQAv2')
# Save to data/raw/
```

Method B - Manual:

- Visit: https://visualqa.org/download.html
- Download train/val questions, annotations, and COCO images
- Extract to `data/raw/`

3. **Open Training Notebook**

```bash
# In VSCode, open:
notebooks/03_model_training.ipynb
```

4. **Run All Cells**

- Click "Run All" or execute cells sequentially
- Training will start automatically
- Wait for completion (~2-4 hours on GPU)

5. **Check Outputs**

```bash
# Model configuration (USE THIS FOR UI):
outputs/model_config.json

# Trained model:
models/final/blip_vqa_visually_impaired_v1/

# Checkpoints:
models/checkpoints/
```

## 🎯 Key Files You Need

1. **`outputs/model_config.json`** ← **MOST IMPORTANT**
   - Contains all specs for building UI
   - API input/output formats
   - Preprocessing requirements
   - Performance metrics

2. **`models/final/`**
   - Your trained model
   - Use this for inference

3. **`src/config.py`**
   - Adjust hyperparameters here
   - Change model, batch size, epochs, etc.

## 🧪 Quick Test (15 minutes)

For quick testing with limited data:

```python
# In the notebook, modify data loading:
train_loader, val_loader = create_dataloaders(
    processor=processor,
    train_max_samples=1000,  # Only 1000 samples
    val_max_samples=500      # Only 500 samples
)

# Reduce epochs:
config.training.num_epochs = 2

# Then run training
```

This will complete in ~15-20 minutes and help you verify everything works.

## 📊 What to Expect

### Training Time

- **Full Dataset**: 3-5 hours (1 epoch) on NVIDIA V100
- **Quick Test** (1000 samples): 15-20 minutes

### Expected Accuracy

- Target: >80% on VQA v2 validation set
- Typical: 78-85% after 10 epochs

### Memory Requirements

- GPU: 12-16GB VRAM
- RAM: 16GB+
- Disk: 20GB+ (for dataset)

## 🔧 Configuration Cheat Sheet

### Model Selection

```python
# BLIP (Recommended)
config.model.model_name = "Salesforce/blip-vqa-base"

# ViLT (Alternative)
config.model.model_name = "dandelin/vilt-b32-finetuned-vqa"
```

### Training Speed

```python
# Faster training (lower accuracy)
config.training.batch_size = 64
config.training.num_epochs = 5

# Better accuracy (slower)
config.training.batch_size = 16
config.training.num_epochs = 15
```

### Memory Optimization

```python
# If running out of GPU memory:
config.training.batch_size = 8
config.training.gradient_accumulation_steps = 4
config.training.use_fp16 = True
```

## ✅ Checklist

Before starting:

- [ ] Python 3.8+ installed
- [ ] CUDA installed (if using GPU)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Data downloaded to `data/raw/`
- [ ] VSCode with Jupyter extension

After training:

- [ ] `model_config.json` generated
- [ ] Model saved to `models/final/`
- [ ] Accuracy >80% achieved
- [ ] Inference tested successfully

---

**Need Help?** Check the full README or troubleshooting section!
