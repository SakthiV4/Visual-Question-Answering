"""
test_aus_and_timer.py
═══════════════════════════════════════════════════════════════
Metric 3 – Task Completion Time & Accessible Usability Scale
═══════════════════════════════════════════════════════════════

Two tools in one file:

  A) AUS Questionnaire (10-item, scored 0-100)
     Run as an interactive CLI survey for each participant.
     Results are saved to aus_results.csv automatically.

  B) Task Timer Recorder
     Manually log how many seconds each participant took
     from "open camera" to "Good frame detected" cue.
     Results are saved to timer_results.csv.

  C) Summary Report
     Combine both CSVs into a paper-ready summary table.

USAGE
-----
# Run the AUS questionnaire (interactive)
python test_aus_and_timer.py --mode aus

# Log task completion times (enter seconds per participant)
python test_aus_and_timer.py --mode timer

# Print summary of all collected data
python test_aus_and_timer.py --mode summary

REQUIREMENTS
------------
pip install tabulate
"""

import argparse
import csv
import os
import sys
from datetime import datetime

try:
    from tabulate import tabulate
except ImportError:
    def tabulate(data, headers=(), tablefmt="plain", **kw):
        rows = [headers] + [list(r) for r in data] if headers else [list(r) for r in data]
        col_widths = [max(len(str(cell)) for cell in col) for col in zip(*rows)]
        lines = []
        for row in rows:
            lines.append("  ".join(str(c).ljust(w) for c, w in zip(row, col_widths)))
        return "\n".join(lines)


# ═══════════════════════════════════════════════
#  AUS QUESTIONS (identical scoring to SUS)
#  Odd  = positive statements  → score val-1
#  Even = negative statements  → score 5-val
# ═══════════════════════════════════════════════

AUS_QUESTIONS = [
    (1, "+", "I think that I would like to use this app frequently."),
    (2, "−", "I found the app unnecessarily complex."),
    (3, "+", "I thought the app was easy to use."),
    (4, "−", "I think that I would need technical support to use this app."),
    (5, "+", "I found the various accessibility functions well integrated."),
    (6, "−", "I thought there was too much inconsistency in the audio guidance."),
    (7, "+", "I would imagine that most people would learn to use this app quickly."),
    (8, "−", "I found the audio feedback system very cumbersome."),
    (9, "+", "I felt very confident using this app independently."),
    (10,"−", "I needed to learn a lot before I could get going with this app."),
]

AUS_CSV = "aus_results.csv"
TIMER_CSV = "timer_results.csv"


def grade_aus(score: float) -> str:
    if score >= 90: return "🏆 Exceptional (Best in Class)"
    if score >= 80: return "✅ Excellent"
    if score >= 68: return "👍 Above Average"
    if score >= 51: return "⚠️  Below Average"
    return "❌ Poor Usability"


# ═══════════════════════════════════════════════
#  A) AUS QUESTIONNAIRE
# ═══════════════════════════════════════════════

def run_aus():
    print("\n" + "═" * 60)
    print("  Accessible Usability Scale (AUS) — Data Collection")
    print("  Rate each statement: 1 = Strongly Disagree · 5 = Strongly Agree")
    print("═" * 60)

    participant_id = input("\n  Participant ID (e.g. P1): ").strip() or "P?"
    responses = {}

    for num, polarity, text in AUS_QUESTIONS:
        while True:
            raw = input(f"\n  Q{num} [{polarity}] {text}\n  Your rating (1-5): ").strip()
            if raw in {"1", "2", "3", "4", "5"}:
                responses[num] = int(raw)
                break
            print("  ⚠  Please enter a number between 1 and 5.")

    # Score: odd → val-1, even → 5-val; sum × 2.5
    total = 0
    for num, polarity, _ in AUS_QUESTIONS:
        v = responses[num]
        total += (v - 1) if polarity == "+" else (5 - v)
    aus_score = round(total * 2.5, 1)

    print("\n" + "═" * 60)
    print(f"  AUS Score for {participant_id}: {aus_score}/100")
    print(f"  Grade: {grade_aus(aus_score)}")
    print("═" * 60 + "\n")

    # Save to CSV
    file_exists = os.path.exists(AUS_CSV)
    with open(AUS_CSV, "a", newline="", encoding="utf-8") as f:
        fields = ["timestamp", "participant_id", "aus_score"] + [f"q{n}" for n in range(1, 11)]
        writer = csv.DictWriter(f, fieldnames=fields)
        if not file_exists:
            writer.writeheader()
        row = {
            "timestamp":      datetime.now().isoformat(),
            "participant_id": participant_id,
            "aus_score":      aus_score,
        }
        for n in range(1, 11):
            row[f"q{n}"] = responses[n]
        writer.writerow(row)

    print(f"  💾 Saved to {AUS_CSV}\n")
    return aus_score


# ═══════════════════════════════════════════════
#  B) TASK TIMER RECORDER
# ═══════════════════════════════════════════════

def run_timer():
    print("\n" + "═" * 60)
    print("  Task Completion Time — Data Collection")
    print("  Measure seconds from camera open to 'Good frame' cue.")
    print("═" * 60)

    participant_id = input("\n  Participant ID (e.g. P1): ").strip() or "P?"

    times = []
    trial = 1
    while True:
        raw = input(f"\n  Trial {trial} — Enter seconds taken (or 'done' to finish): ").strip()
        if raw.lower() in {"done", "d", "q", "quit", "exit"}:
            break
        try:
            t = float(raw)
            times.append(t)
            print(f"  ✅ Logged {t}s")
            trial += 1
        except ValueError:
            print("  ⚠  Enter a number (e.g. 12.5) or 'done'.")

    if not times:
        print("  No times recorded.\n")
        return

    avg = sum(times) / len(times)
    print(f"\n  Participant {participant_id}: {len(times)} trial(s)")
    print(f"  Average: {avg:.1f}s   Min: {min(times):.1f}s   Max: {max(times):.1f}s\n")

    file_exists = os.path.exists(TIMER_CSV)
    with open(TIMER_CSV, "a", newline="", encoding="utf-8") as f:
        fields = ["timestamp", "participant_id", "trial", "seconds"]
        writer = csv.DictWriter(f, fieldnames=fields)
        if not file_exists:
            writer.writeheader()
        for i, t in enumerate(times, 1):
            writer.writerow({
                "timestamp":      datetime.now().isoformat(),
                "participant_id": participant_id,
                "trial":          i,
                "seconds":        t,
            })

    print(f"  💾 Saved to {TIMER_CSV}\n")


# ═══════════════════════════════════════════════
#  C) SUMMARY REPORT
# ═══════════════════════════════════════════════

def run_summary():
    print("\n" + "═" * 66)
    print("  METRIC 3 — Summary Report")
    print("═" * 66)

    # ── AUS Summary ───────────────────────────────────────────────
    if os.path.exists(AUS_CSV):
        with open(AUS_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if rows:
            scores = [float(r["aus_score"]) for r in rows]
            avg_aus = sum(scores) / len(scores)
            print(f"\n  📋 AUS Questionnaire  ({len(rows)} participants)")
            tbl = [[r["participant_id"], r["aus_score"], grade_aus(float(r["aus_score"]))]
                   for r in rows]
            print(tabulate(tbl, headers=["Participant", "AUS Score", "Grade"],
                           tablefmt="rounded_outline"))
            print(f"\n  Group Average AUS Score : {avg_aus:.1f}/100")
            print(f"  Group Grade             : {grade_aus(avg_aus)}")
        else:
            print("\n  AUS CSV is empty.")
    else:
        print(f"\n  ⚠  {AUS_CSV} not found. Run --mode aus first.")

    # ── Timer Summary ─────────────────────────────────────────────
    if os.path.exists(TIMER_CSV):
        with open(TIMER_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if rows:
            from collections import defaultdict
            by_p = defaultdict(list)
            for r in rows:
                by_p[r["participant_id"]].append(float(r["seconds"]))

            print(f"\n\n  ⏱️  Task Completion Time  ({len(by_p)} participants)")
            tbl = []
            all_times = []
            for pid, times in sorted(by_p.items()):
                all_times.extend(times)
                tbl.append([
                    pid,
                    len(times),
                    f"{min(times):.1f}",
                    f"{max(times):.1f}",
                    f"{sum(times)/len(times):.1f}",
                ])
            print(tabulate(tbl,
                           headers=["Participant", "Trials", "Min (s)", "Max (s)", "Avg (s)"],
                           tablefmt="rounded_outline"))
            overall_avg = sum(all_times) / len(all_times)
            print(f"\n  Overall Average Task Completion Time : {overall_avg:.1f} seconds")
        else:
            print("\n  Timer CSV is empty.")
    else:
        print(f"\n  ⚠  {TIMER_CSV} not found. Run --mode timer first.")

    print("\n" + "═" * 66 + "\n")


# ═══════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Metric 3 – AUS questionnaire + Task Completion Time logger"
    )
    parser.add_argument(
        "--mode",
        choices=["aus", "timer", "summary"],
        required=True,
        help="aus = run questionnaire | timer = log times | summary = show report",
    )
    args = parser.parse_args()

    if args.mode == "aus":
        run_aus()
        another = input("  Run for another participant? (y/n): ").strip().lower()
        while another == "y":
            run_aus()
            another = input("  Another? (y/n): ").strip().lower()
        run_summary()

    elif args.mode == "timer":
        run_timer()
        another = input("  Log for another participant? (y/n): ").strip().lower()
        while another == "y":
            run_timer()
            another = input("  Another? (y/n): ").strip().lower()
        run_summary()

    elif args.mode == "summary":
        run_summary()


if __name__ == "__main__":
    main()
