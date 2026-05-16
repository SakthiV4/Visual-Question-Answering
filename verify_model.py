
import os
import sys
import torch
from torch.utils.data import DataLoader
from transformers import BlipProcessor, BlipForQuestionAnswering
from tqdm import tqdm
from pathlib import Path

# Add current directory to path
sys.path.append(os.getcwd())

# 1. Setup Config & Paths (Before importing imports that rely on them)
import src.config
# Monkey-patch RAW_DATA_DIR to point to where the user's data actually is
src.config.RAW_DATA_DIR = Path("data/vqa_v2_50k")

# 2. Import Dataset (It imports RAW_DATA_DIR, so we patch it too)
import src.data.dataset
from src.data.dataset import VQADataset
from src.data.dataloader import collate_fn

# Patch dataset module's RAW_DATA_DIR
src.data.dataset.RAW_DATA_DIR = Path("data/vqa_v2_50k")

# Check model path
if os.path.exists("backend/model/model.safetensors"):
    MODEL_PATH = "backend/model"
elif os.path.exists("models/local_blip/model.safetensors"):
    MODEL_PATH = "models/local_blip"
else:
    print("❌ Model not found in backend/model or models/local_blip")
    sys.exit(1)

def verify():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🚀 Verifying model from: {MODEL_PATH}")
    print(f"📁 Data Dir: {src.data.dataset.RAW_DATA_DIR}")
    print(f"🖥️  Device: {device}")
    
    # Load Model
    try:
        processor = BlipProcessor.from_pretrained(MODEL_PATH)
        model = BlipForQuestionAnswering.from_pretrained(MODEL_PATH).to(device)
        model.eval()
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    # Load Val Data
    print("📥 Loading Validation Data...")
    
    try:
        val_ds = VQADataset(
            split="val", 
            processor=processor,
            max_samples=None 
        )
    except FileNotFoundError as e:
        print(f"❌ Data not found: {e}")
        print("Please ensure 'data/vqa_v2_50k' contains 'val2014' and annotation JSONs.")
        return
    
    val_dl = DataLoader(
        val_ds, 
        batch_size=32, 
        shuffle=False, 
        collate_fn=collate_fn, 
        num_workers=0
    )
    
    correct = 0
    total = 0
    
    print(f"🔍 Checking {len(val_ds)} images...")
    
    with torch.no_grad():
        for batch in tqdm(val_dl):
            if "encoding" in batch:
                inputs = batch["encoding"]
                for k, v in inputs.items():
                    if isinstance(v, torch.Tensor):
                        inputs[k] = v.to(device)
                
                out = model.generate(**inputs, max_new_tokens=10)
                predictions = processor.batch_decode(out, skip_special_tokens=True)
            else:
                continue

            answers = batch["answers"]
            
            for pred, true_ans in zip(predictions, answers):
                # VQA dataset returns 'answer' as the most frequent string
                if pred.strip().lower() == true_ans.strip().lower():
                    correct += 1
                total += 1
                
    if total > 0:
        acc = (correct / total) * 100
        print("\n" + "="*40)
        print(f"📊 Final Validation Accuracy: {acc:.2f}%")
        print("="*40)
    else:
        print("⚠️ No samples checked.")

if __name__ == "__main__":
    verify()
