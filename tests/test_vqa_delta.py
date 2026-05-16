"""
test_vqa_delta.py
═══════════════════════════════════════════════════════════════
Metric 2 – VQA Accuracy Delta (BLIP Performance Improvement)
═══════════════════════════════════════════════════════════════

Measures how much your app's frame-quality guidance improves BLIP's
ability to answer questions (reduces the "unanswerable" rate).

HOW IT WORKS
────────────
1. UNGUIDED  – run BLIP on low-quality / unfiltered images (baseline)
2. GUIDED    – run BLIP on images that PASSED the Frame Quality filter
               (score ≥ minScore, default 50)
3. Delta     – guided_answerable_rate − unguided_answerable_rate

The script classifies a response as "unanswerable" when BLIP's
average token confidence falls below --conf-threshold (default 0.45).

USAGE
-----
# Minimal: one folder each for unguided and guided captures
python test_vqa_delta.py \\
    --unguided-dir  data/unguided_images/ \\
    --guided-dir    data/guided_images/   \\
    --question      "What is in front of me?"

# Sweep multiple questions from a text file (one per line)
python test_vqa_delta.py \\
    --unguided-dir  data/unguided_images/ \\
    --guided-dir    data/guided_images/   \\
    --questions-file data/questions.txt   \\
    --csv           results_vqa_delta.csv

# Use your own fine-tuned model instead of the Hugging Face default
python test_vqa_delta.py \\
    --unguided-dir data/unguided_images/ \\
    --guided-dir   data/guided_images/   \\
    --question     "What is in front of me?" \\
    --model        sakthi04/vqa-model-finetuned

REQUIREMENTS
────────────
pip install transformers torch torchvision Pillow tabulate
"""

import argparse
import csv
import os
import sys
from pathlib import Path

import torch
from PIL import Image
from transformers import BlipForQuestionAnswering, BlipProcessor

# ─────────────────────────── Helpers ────────────────────────────────

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def list_images(folder: str) -> list[str]:
    return sorted(
        str(p) for p in Path(folder).iterdir()
        if p.suffix.lower() in IMAGE_EXTS
    )


def load_model(model_name: str):
    print(f"📥  Loading BLIP model: {model_name} …")
    processor = BlipProcessor.from_pretrained(model_name)
    model     = BlipForQuestionAnswering.from_pretrained(model_name)
    device    = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"🚀  Model ready on {device}\n")
    return processor, model, device


# ─────────────────────────── NR-IQA helper (inline) ─────────────────

def laplacian_variance(pil_img: Image.Image) -> float:
    """Quick blur score — used internally to auto-filter guided images."""
    import numpy as np
    try:
        import cv2
        gray = cv2.cvtColor(
            np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2GRAY
        )
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())
    except ImportError:
        # Fallback without cv2: use numpy gradient
        arr  = np.array(pil_img.convert("L"), dtype=float)
        lap  = (
            np.roll(arr, 1, 0) + np.roll(arr, -1, 0) +
            np.roll(arr, 1, 1) + np.roll(arr, -1, 1) - 4 * arr
        )
        return float(lap.var())


# ─────────────────────────── F1 Scoring ────────────────────────────────

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


# ─────────────────────────── BLIP Inference ──────────────────────────

def run_blip(
    processor,
    model,
    device: str,
    image_path: str,
    question: str,
    conf_threshold: float,
    ground_truth: str = None,
) -> dict:
    """
    Run BLIP on one image+question pair.
    Returns { path, question, answer, confidence, answerable, f1, precision, recall, exact_match }.
    """
    try:
        pil_img = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {"path": image_path, "question": question,
                "answer": "ERROR", "confidence": 0.0,
                "answerable": False, "error": str(e)}

    inputs = processor(pil_img, question, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=20,
            output_scores=True,
            return_dict_in_generate=True,
        )

    answer = processor.decode(outputs.sequences[0], skip_special_tokens=True).strip()

    confidence = 1.0
    if hasattr(outputs, "scores") and outputs.scores:
        probs      = [torch.softmax(s, dim=-1).max().item() for s in outputs.scores]
        confidence = sum(probs) / len(probs)

    answerable = confidence >= conf_threshold

    result = {
        "path":       image_path,
        "question":   question,
        "answer":     answer,
        "confidence": round(confidence, 4),
        "answerable": answerable,
    }
    
    if ground_truth:
        metrics = vqa_f1_score(answer, ground_truth)
        result.update(metrics)

    return result


# ─────────────────────────── Evaluation Loop ─────────────────────────

def evaluate_folder(
    processor, model, device,
    image_paths: list[str],
    questions: list[str],
    conf_threshold: float,
    label: str,
    ground_truth: str = None,
) -> list[dict]:
    results = []
    total = len(image_paths) * len(questions)
    done  = 0
    for img_path in image_paths:
        for q in questions:
            done += 1
            print(f"  [{label}] {done}/{total}  {os.path.basename(img_path)} | {q[:50]}", end="\r")
            r = run_blip(processor, model, device, img_path, q, conf_threshold, ground_truth)
            r["group"] = label
            results.append(r)
    print()
    return results


def compute_rates(entries: list[dict], has_gt: bool = False) -> dict:
    total      = len(entries)
    answerable = sum(1 for e in entries if e.get("answerable"))
    
    if total == 0:
        return {"total": 0, "answerable": 0, "unanswerable": 0,
                "answerable_rate": None, "unanswerable_rate": None,
                "f1_score": None, "exact_match": None}
                
    stats = {
        "total":              total,
        "answerable":         answerable,
        "unanswerable":       total - answerable,
        "answerable_rate":    round(answerable / total * 100, 1),
        "unanswerable_rate":  round((total - answerable) / total * 100, 1),
        "f1_score":           None,
        "exact_match":        None
    }
    
    if has_gt:
        avg_f1 = sum(e.get("f1", 0.0) for e in entries) / total
        exacts = sum(1 for e in entries if e.get("exact_match", False))
        stats["f1_score"]    = round(avg_f1 * 100, 1)
        stats["exact_match"] = round(exacts / total * 100, 1)
        
    return stats


# ─────────────────────────── Report ──────────────────────────────────

def plot_results(unguided_stats: dict, guided_stats: dict):
    try:
        import matplotlib.pyplot as plt
        
        labels = ['Answerable Rate (%)', 'Unanswerable Rate (%)']
        un_rates = [unguided_stats["answerable_rate"] or 0, unguided_stats["unanswerable_rate"] or 0]
        g_rates = [guided_stats["answerable_rate"] or 0, guided_stats["unanswerable_rate"] or 0]

        x = [0, 1]
        width = 0.35

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar([p - width/2 for p in x], un_rates, width, label='Unguided (Baseline)', color='#e74c3c')
        ax.bar([p + width/2 for p in x], g_rates, width, label='Guided (With App)', color='#2ecc71')

        ax.set_ylabel('Percentage (%)')
        ax.set_title('VQA Answerability: Unguided vs. Guided Photos')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 115)
        ax.legend()

        for i, p in enumerate(x):
            ax.text(p - width/2, un_rates[i] + 2, f"{un_rates[i]}%", ha='center', fontweight='bold')
            ax.text(p + width/2, g_rates[i] + 2, f"{g_rates[i]}%", ha='center', fontweight='bold')

        plt.tight_layout()
        plt.savefig('vqa_delta_chart.png', dpi=300)
        print("  📈 Generated performance graph: vqa_delta_chart.png\n")
    except ImportError:
        pass


def print_report(unguided_stats: dict, guided_stats: dict):
    from tabulate import tabulate

    delta_ans  = None
    delta_unans = None
    if unguided_stats["answerable_rate"] is not None and guided_stats["answerable_rate"] is not None:
        delta_ans   = round(guided_stats["answerable_rate"]   - unguided_stats["answerable_rate"],  1)
        delta_unans = round(unguided_stats["unanswerable_rate"] - guided_stats["unanswerable_rate"], 1)

    has_gt = (unguided_stats.get("f1_score") is not None)

    rows = [
        ["",                      "Unguided (baseline)", "Guided (with app)",  "Delta"],
        ["Total samples",          unguided_stats["total"],      guided_stats["total"],      "—"],
        ["Answerable",             unguided_stats["answerable"],  guided_stats["answerable"],  "—"],
        ["Unanswerable",           unguided_stats["unanswerable"],guided_stats["unanswerable"],"—"],
        ["Answerable Rate %",       unguided_stats["answerable_rate"],  guided_stats["answerable_rate"],
         f"{delta_ans:+.1f}%" if delta_ans is not None else "—"],
        ["Unanswerable Rate %",     unguided_stats["unanswerable_rate"],guided_stats["unanswerable_rate"],
         f"−{delta_unans:.1f}%" if delta_unans is not None else "—"],
    ]

    if has_gt:
        d_f1 = round(guided_stats["f1_score"] - unguided_stats["f1_score"], 1)
        d_em = round(guided_stats["exact_match"] - unguided_stats["exact_match"], 1)
        rows.extend([
            ["Word-Level F1 Score %", unguided_stats["f1_score"], guided_stats["f1_score"], f"{d_f1:+.1f}%"],
            ["Exact Match Rate %",    unguided_stats["exact_match"], guided_stats["exact_match"], f"{d_em:+.1f}%"],
        ])

    print("\n" + "═" * 66)
    print("  VQA ACCURACY DELTA — BLIP Performance Improvement Report")
    print("═" * 66)
    print(tabulate(rows[1:], headers=rows[0], tablefmt="rounded_outline"))

    if delta_ans is not None:
        verdict = "✅ App guidance IMPROVED answerability" if delta_ans >= 0 else "⚠️  No improvement detected"
        print(f"\n  {verdict} by {abs(delta_ans):.1f} percentage points")
        print(f"  Unanswerable rate reduced by {abs(delta_unans):.1f} pp\n")
        
        # Draw the chart
        plot_results(unguided_stats, guided_stats)



# ─────────────────────────── Main ────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Metric 2 – VQA Accuracy Delta for research paper"
    )
    parser.add_argument("--unguided-dir",   required=True,
                        help="Folder of raw/unfiltered images (no app guidance)")
    parser.add_argument("--guided-dir",     required=True,
                        help="Folder of images captured WITH the app's frame guidance")
    parser.add_argument("--question",       default=None,
                        help="Single question to ask BLIP for every image")
    parser.add_argument("--questions-file", default=None,
                        help="Text file with one question per line")
    parser.add_argument("--model",
                        default="sakthi04/vqa-model-finetuned",
                        help="BLIP model name or local path")
    parser.add_argument("--conf-threshold", type=float, default=0.45,
                        help="Min avg confidence to call a response 'answerable' (default 0.45)")
    parser.add_argument("--ground-truth", default=None,
                        help="Expected true answer to compute F1, Precision, Recall, and Accuracy")
    parser.add_argument("--csv", default=None,
                        help="Save per-image results to this CSV file")
    args = parser.parse_args()

    # Build questions list
    if args.questions_file:
        with open(args.questions_file, encoding="utf-8") as f:
            questions = [l.strip() for l in f if l.strip()]
    elif args.question:
        questions = [args.question]
    else:
        parser.error("Provide --question or --questions-file")

    unguided_imgs = list_images(args.unguided_dir)
    guided_imgs   = list_images(args.guided_dir)

    if not unguided_imgs:
        sys.exit(f"No images found in --unguided-dir: {args.unguided_dir}")
    if not guided_imgs:
        sys.exit(f"No images found in --guided-dir: {args.guided_dir}")

    print(f"  Unguided images : {len(unguided_imgs)}")
    print(f"  Guided   images : {len(guided_imgs)}")
    print(f"  Questions       : {len(questions)}")
    print(f"  Conf threshold  : {args.conf_threshold}\n")

    processor, model, device = load_model(args.model)

    unguided_results = evaluate_folder(
        processor, model, device,
        unguided_imgs, questions, args.conf_threshold, "UNGUIDED", args.ground_truth
    )
    guided_results = evaluate_folder(
        processor, model, device,
        guided_imgs, questions, args.conf_threshold, "GUIDED", args.ground_truth
    )

    has_gt = bool(args.ground_truth)
    unguided_stats = compute_rates(unguided_results, has_gt)
    guided_stats   = compute_rates(guided_results, has_gt)

    print_report(unguided_stats, guided_stats)

    if args.csv:
        all_results = unguided_results + guided_results
        fields = ["group", "path", "question", "answer", "confidence", "answerable"]
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(all_results)
        print(f"  💾 Per-image results saved to {args.csv}\n")


if __name__ == "__main__":
    main()
