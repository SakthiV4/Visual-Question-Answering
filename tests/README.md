# VQA Paper Metrics — Test Scripts

Three standalone Python scripts to generate the metric values for your research paper. **None of these touch the web app.**

---

## Setup (one-time)

```bash
pip install opencv-python-headless numpy Pillow torch transformers tabulate
```

---

## Metric 1 — Frame Quality Score (NR-IQA)

```bash
# Single image
python tests/test_frame_quality.py --image path/to/photo.jpg

# Whole folder → CSV
python tests/test_frame_quality.py --folder data/test_images/ --csv results_frame.csv
```

**Output:** `frameScore/100`, blur penalty, lighting penalty, framing penalty, suggestion text.

---

## Metric 2 — VQA Accuracy Delta

Prepare two folders:
- `data/unguided_images/` — photos taken **without** the app's guidance (blurry, dark, off-centre)
- `data/guided_images/`   — photos taken **with** the app's audio guidance (good quality)

```bash
python tests/test_vqa_delta.py \
    --unguided-dir data/unguided_images/ \
    --guided-dir   data/guided_images/ \
    --question     "What is in front of me?" \
    --csv          results_vqa_delta.csv
```

**Output:** answerability rate for each group + **delta %** (the key paper metric).

---

## Metric 3 — Task Completion Time & AUS

```bash
# Step 1: Record how long each participant takes (in seconds)
python tests/test_aus_and_timer.py --mode timer

# Step 2: Administer the AUS questionnaire to each participant
python tests/test_aus_and_timer.py --mode aus

# Step 3: Print a full summary table
python tests/test_aus_and_timer.py --mode summary
```

Results are auto-saved to `aus_results.csv` and `timer_results.csv` in the current directory.

**AUS scoring:** Sum of (odd Q: val−1, even Q: 5−val) × 2.5 → score out of 100.  
Score ≥ 68 = above average · ≥ 80 = excellent · ≥ 90 = exceptional.
