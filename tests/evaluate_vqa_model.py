"""
evaluate_vqa_model.py
═══════════════════════════════════════════════════════════════
Evaluates a finetuned BLIP VQA model against a standard 
validation subset of the VQA v2 dataset.

Calculates:
  • Exact Match Accuracy
  • Word-Level Precision
  • Word-Level Recall
  • Word-Level F1 Score

Generates a performance graph (vqa_model_performance.png).

USAGE:
python evaluate_vqa_model.py --model sakthi04/vqa-model-finetuned --samples 100
"""

import argparse
import sys
import os
import torch
from transformers import BlipForQuestionAnswering, BlipProcessor
from datasets import load_dataset
from tabulate import tabulate
import matplotlib.pyplot as plt

def vqa_f1_score(predicted: str, ground_truth: str) -> dict:
    if not ground_truth:
        return {"f1": 0.0, "precision": 0.0, "recall": 0.0, "exact_match": False}
    
    pred_tokens = set(predicted.lower().split())
    gt_tokens = set(ground_truth.lower().split())
    
    exact_match = (predicted.lower().strip() == ground_truth.lower().strip())
    
    if not pred_tokens or not gt_tokens:
        return {"f1": 0.0, "precision": 0.0, "recall": 0.0, "exact_match": exact_match}
        
    common = pred_tokens.intersection(gt_tokens)
    if not common:
        return {"f1": 0.0, "precision": 0.0, "recall": 0.0, "exact_match": exact_match}
        
    prec = len(common) / len(pred_tokens)
    rec  = len(common) / len(gt_tokens)
    f1   = 2 * (prec * rec) / (prec + rec)
    
    return {"f1": f1, "precision": prec, "recall": rec, "exact_match": exact_match}


def main():
    parser = argparse.ArgumentParser(description="Evaluate VQA Model Performance")
    parser.add_argument("--model", default="sakthi04/vqa-model-finetuned", help="HuggingFace model ID")
    parser.add_argument("--samples", type=int, default=100, help="Number of samples to evaluate")
    args = parser.parse_args()

    # 1. Load Model
    print(f"[+] Loading BLIP model: {args.model} ...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = BlipProcessor.from_pretrained(args.model)
    model = BlipForQuestionAnswering.from_pretrained(args.model).to(device)
    print(f"[*] Model ready on {device}")

    # 2. Load Dataset (local subset)
    print("\n[+] Loading VQA dataset (local validation split) ...")
    local_json = "data/local_vqa_val.json"
    if not os.path.exists(local_json):
        print(f"[!] File not found: {local_json}")
        sys.exit(1)
        
    import json
    with open(local_json, "r") as f:
        dataset = json.load(f)

    print(f"[+] Evaluating on {args.samples} samples...")
    
    total = 0
    exact_matches = 0
    total_f1 = 0.0
    total_precision = 0.0
    total_recall = 0.0

    # 3. Evaluation Loop
    from PIL import Image
    for idx, item in enumerate(dataset):
        if idx >= args.samples:
            break
            
        try:
            image = Image.open(item["image"]).convert("RGB")
        except:
            continue
            
        question = item["question"]
        
        answers = [ans["answer"] for ans in item["answers"]]
        ground_truth = max(set(answers), key=answers.count) if answers else ""
        
        # Inference
        inputs = processor(image, question, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=20)
        
        predicted = processor.decode(outputs[0], skip_special_tokens=True).strip()
        
        # Score
        metrics = vqa_f1_score(predicted, ground_truth)
        
        if metrics["exact_match"]:       exact_matches += 1
        total_f1        += metrics["f1"]
        total_precision += metrics["precision"]
        total_recall    += metrics["recall"]
        total += 1
        
        print(f"\r  Progress: {total}/{args.samples} (F1: {total_f1/total:.2f})", end="")

    print("\n\n------------------------------------------------------------------")
    print("  MODEL EVALUATION RESULTS")
    print("------------------------------------------------------------------")
    
    avg_f1    = total_f1 / total
    avg_prec  = total_precision / total
    avg_rec   = total_recall / total
    exact_pct = exact_matches / total
    
    rows = [
        ["Metric", "Score"],
        ["Samples Evaluated", f"{total}"],
        ["Exact Match Accuracy", f"{exact_pct*100:.1f}%"],
        ["Word-Level Precision", f"{avg_prec*100:.1f}%"],
        ["Word-Level Recall",    f"{avg_rec*100:.1f}%"],
        ["Word-Level F1 Score",  f"{avg_f1*100:.1f}%"],
    ]
    
    with open("f1_summary.txt", "w") as f:
        f.write("MODEL EVALUATION RESULTS\n")
        f.write("------------------------\n")
        for r in rows:
            f.write(f"{r[0]}: {r[1]}\n")
            
    print(tabulate(rows[1:], headers=rows[0], tablefmt="plain"))
    
    # 4. Generate Graph
    try:
        metrics_names = ['Exact Match\nAccuracy', 'Precision', 'Recall', 'F1 Score']
        scores = [exact_pct*100, avg_prec*100, avg_rec*100, avg_f1*100]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(metrics_names, scores, color=['#3498db', '#2ecc71', '#f1c40f', '#e74c3c'])
        
        plt.ylim(0, 110)
        plt.ylabel('Percentage (%)')
        plt.title(f'VQA Model Performance ({args.model})')
        
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f"{yval:.1f}%", ha='center', fontweight='bold')
            
        plt.savefig('vqa_model_performance.png', dpi=300)
        print("\n  [+] Generated performance graph: vqa_model_performance.png\n")
    except Exception as e:
        print(f"\n  [!] Failed to generate graph: {e}")

if __name__ == "__main__":
    main()
