"""
test_frame_quality.py
═══════════════════════════════════════════════════════════════
Metric 1 – Frame Quality Score (No-Reference Image Quality Assessment)
═══════════════════════════════════════════════════════════════

Tests images and produces a 0-100 Frame Score decomposed into:
  • Blur Penalty      (0-40)  – Variance of the Laplacian
  • Lighting Penalty  (0-30)  – Histogram brightness & contrast
  • Framing Penalty   (0-30)  – Subject centering via edge energy

USAGE
-----
# Test a single image
python test_frame_quality.py --image path/to/photo.jpg

# Test a whole folder and get a CSV summary
python test_frame_quality.py --folder path/to/images/ --csv results_frame.csv

REQUIREMENTS
------------
pip install opencv-python-headless numpy Pillow tabulate
"""

import argparse
import csv
import os
import sys

import cv2
import numpy as np
from tabulate import tabulate


# ─────────────────────────── Core NR-IQA ────────────────────────────

def compute_frame_score(image_path: str) -> dict:
    """
    Load an image and return a full NR-IQA breakdown.
    Returns a dict with: frameScore, blurPenalty, lightingPenalty,
    framingPenalty, avgBrightness, lapVariance, suggestions, path
    """
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        return {"error": f"Cannot read image: {image_path}", "path": image_path}

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)
    h, w = gray.shape

    # ── 1. Blur Penalty: Variance of the Laplacian ───────────────────
    laplacian     = cv2.Laplacian(gray, cv2.CV_64F)
    lap_variance  = float(laplacian.var())
    # Map: lapVariance < 50 → very blurry (penalty = 40)
    #       lapVariance > 800 → sharp    (penalty = 0)
    blur_penalty  = max(0, min(40, int(40 - (lap_variance / 800) * 40)))

    # ── 2. Lighting Penalty: Brightness & Contrast ───────────────────
    avg_br  = float(gray.mean())
    std_dev = float(gray.std())          # contrast proxy

    lighting_penalty = 0
    if avg_br < 35:        lighting_penalty += 20  # too dark
    elif avg_br < 65:      lighting_penalty += 10  # dim
    elif avg_br > 220:     lighting_penalty += 20  # overexposed
    elif avg_br > 195:     lighting_penalty += 10  # slightly bright
    if std_dev < 20:       lighting_penalty += 10  # low contrast / flat
    lighting_penalty = min(lighting_penalty, 30)

    # ── 3. Framing Penalty: Subject Centering ────────────────────────
    # Compare edge energy in the centre 50% vs border region
    cx0, cx1 = int(w * 0.25), int(w * 0.75)
    cy0, cy1 = int(h * 0.25), int(h * 0.75)

    edges      = cv2.Sobel(gray, cv2.CV_64F, 1, 0)**2 + cv2.Sobel(gray, cv2.CV_64F, 0, 1)**2
    centre_roi = edges[cy0:cy1, cx0:cx1]
    border_mask = np.ones_like(edges, dtype=bool)
    border_mask[cy0:cy1, cx0:cx1] = False
    border_roi  = edges[border_mask]

    c_avg = centre_roi.mean() if centre_roi.size else 0
    b_avg = border_roi.mean()  if border_roi.size  else 0

    if b_avg > c_avg * 1.4:    framing_penalty = 20  # subject cut off
    elif b_avg > c_avg * 1.1:  framing_penalty = 10  # slightly off-centre
    else:                       framing_penalty = 0
    framing_penalty = min(framing_penalty, 30)

    # ── 4. Composite Score ───────────────────────────────────────────
    frame_score = max(0, min(100, 100 - blur_penalty - lighting_penalty - framing_penalty))

    # ── 5. Human-readable guidance messages ──────────────────────────
    suggestions = []
    if blur_penalty > 20:      suggestions.append("Very blurry — hold camera steady / move closer")
    elif blur_penalty > 10:    suggestions.append("Slightly blurry — steady the camera")
    if avg_br < 35:            suggestions.append("Too dark — turn on lights")
    elif avg_br < 65:          suggestions.append("Dim image — improve lighting or use flash")
    elif avg_br > 220:         suggestions.append("Overexposed — move away from direct light")
    if framing_penalty > 15:   suggestions.append("Subject may be cut off — re-centre camera")
    elif framing_penalty > 5:  suggestions.append("Slightly off-centre — adjust framing")
    if not suggestions:        suggestions.append("Good frame — proceed to capture")

    return {
        "path":             image_path,
        "frameScore":       frame_score,
        "blurPenalty":      blur_penalty,
        "lightingPenalty":  lighting_penalty,
        "framingPenalty":   framing_penalty,
        "avgBrightness":    round(avg_br, 1),
        "lapVariance":      round(lap_variance, 1),
        "suggestion":       suggestions[0],
        "allSuggestions":   suggestions,
    }


def grade(score: int) -> str:
    if score >= 80: return "✅ Excellent"
    if score >= 60: return "👍 Good"
    if score >= 45: return "⚠️  Fair"
    return "❌ Poor"


# ─────────────────────────── CLI / Main ─────────────────────────────

def run_single(image_path: str):
    r = compute_frame_score(image_path)
    if "error" in r:
        print(f"ERROR: {r['error']}")
        sys.exit(1)

    print("\n" + "═" * 52)
    print(f"  Frame Quality Score — {os.path.basename(image_path)}")
    print("═" * 52)
    rows = [
        ["Frame Score",       f"{r['frameScore']}/100  {grade(r['frameScore'])}"],
        ["Blur Penalty",      f"-{r['blurPenalty']}/40   (Laplacian var: {r['lapVariance']})"],
        ["Lighting Penalty",  f"-{r['lightingPenalty']}/30   (avg brightness: {r['avgBrightness']})"],
        ["Framing Penalty",   f"-{r['framingPenalty']}/30"],
        ["Suggestion",        r['suggestion']],
    ]
    print(tabulate(rows, tablefmt="plain"))
    print("═" * 52 + "\n")


def run_folder(folder: str, csv_out: str | None):
    exts   = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    paths  = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if os.path.splitext(f)[1].lower() in exts
    ]
    if not paths:
        print(f"No images found in {folder}")
        sys.exit(1)

    results = [compute_frame_score(p) for p in sorted(paths)]
    valid   = [r for r in results if "error" not in r]

    # Pretty table
    headers = ["Image", "Score", "Grade", "Blur", "Lighting", "Framing", "Avg Brightness"]
    rows = [
        [
            os.path.basename(r["path"]),
            r["frameScore"],
            grade(r["frameScore"]),
            f"-{r['blurPenalty']}",
            f"-{r['lightingPenalty']}",
            f"-{r['framingPenalty']}",
            r["avgBrightness"],
        ]
        for r in valid
    ]
    print("\n" + tabulate(rows, headers=headers, tablefmt="rounded_outline"))

    if valid:
        scores = [r["frameScore"] for r in valid]
        print(f"\n  📊 Summary: {len(valid)} images analysed")
        print(f"     Average Score : {sum(scores)/len(scores):.1f}")
        print(f"     Best          : {max(scores)}  ({os.path.basename(valid[scores.index(max(scores))]['path'])})")
        print(f"     Worst         : {min(scores)}  ({os.path.basename(valid[scores.index(min(scores))]['path'])})\n")

    if csv_out:
        fieldnames = ["path", "frameScore", "blurPenalty", "lightingPenalty",
                      "framingPenalty", "avgBrightness", "lapVariance", "suggestion"]
        with open(csv_out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            w.writerows(valid)
        print(f"  💾 Results saved to {csv_out}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Frame Quality Score – No-Reference IQA for VQA paper"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image",  help="Path to a single image file")
    group.add_argument("--folder", help="Path to a folder of images")
    parser.add_argument("--csv",   help="(Folder mode) Save results to this CSV file")
    args = parser.parse_args()

    if args.image:
        run_single(args.image)
    else:
        run_folder(args.folder, args.csv)


if __name__ == "__main__":
    main()
