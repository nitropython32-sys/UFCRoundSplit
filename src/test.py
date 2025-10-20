import json
import re

import subprocess


def clock_to_seconds(clock_str):
    """Convert mm:ss or m.ss to seconds."""
    clock_str = str(clock_str)
    clock_str = clock_str.replace(".", ":")
    parts = clock_str.split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(clock_str)

def get_round(entry):
    """Extract current round number."""
    model = json.loads(entry["model_response"])
    val = str(model.get("round", "")).strip()
    m = re.search(r"(\d+)", val)
    return int(m.group(1)) if m else None

def get_clock(entry):
    """Extract clock time (time left in round)."""
    model = json.loads(entry["model_response"])
    return clock_to_seconds(model.get("time", 0))

# --- Load data ---
with open("/home/nigel/Desktop/Projects/UFCRoundSplit/results.json", "r") as f:
    data = json.load(f)

body = data["results"]

# --- Group by round ---
rounds = {}
for entry in body:
    rnd = get_round(entry)
    if rnd is None:
        continue
    rounds.setdefault(rnd, []).append(entry)

# --- Compute cut ranges ---
cuts = []
for rnd, entries in sorted(rounds.items()):
    starts = []
    for e in entries:
        raw = e["raw_time_seconds"]
        left = get_clock(e)
        # Estimate round start time
        start_est = raw - (300 - left) if left <= 300 else raw
        starts.append(start_est)
    start_time = max(0, min(starts))
    cuts.append({
        "round": rnd,
        "start_sec": start_time
    })

# --- Infer end times from next round starts ---
for i in range(len(cuts)):
    if i < len(cuts) - 1:
        cuts[i]["end_sec"] = cuts[i + 1]["start_sec"]
    else:
        cuts[i]["end_sec"] = float(data["header"]["total_frames"]) / 30.0  # rough estimate if fps ~30

# --- Print result ---
for c in cuts:
    print(f"Round {c['round']}: {c['start_sec']:.2f}s → {c['end_sec']:.2f}s")


# ####now lets cut the video. 

# input_path = "/home/nigel/Desktop/Projects/UFCRoundSplit/Fights/Yair Rodriguez vs The Korean Zombie Full Fight - EA Alter Egos： Prime Series 3 [W4-LEgjxokI].mp4"
# output_path = "round1_trimmed.mp4"

# # Hardcode first cut (round 1)
# start = str(cuts[0]["start_sec"])
# end = str(cuts[0]["end_sec"])

# cmd = [
#     "ffmpeg",
#     "-y",
#     "-ss", start,
#     "-to", end,
#     "-i", input_path,
#     "-c", "copy",
#     output_path
# ]

# result = subprocess.run(cmd, capture_output=True, text=True)

# print("STDOUT:", result.stdout)
# print("STDERR:", result.stderr)
import subprocess
import os

input_path = "/home/nigel/Desktop/Projects/UFCRoundSplit/Fights/Yair Rodriguez vs The Korean Zombie Full Fight - EA Alter Egos： Prime Series 3 [W4-LEgjxokI].mp4"

# Loop through all cuts and export one video per round
for c in cuts:
    start = str(c["start_sec"])
    end = str(c["end_sec"])
    round_num = c["round"]

    output_path = f"round_{round_num}.mp4"
    print(f"⏱️ Cutting Round {round_num}: {start}s → {end}s")

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", start,
        "-to", end,
        "-i", input_path,
        "-c", "copy",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Optional: log result
    if result.returncode == 0:
        print(f"✅ Saved {output_path}")
    else:
        print(f"⚠️ Error on round {round_num}: {result.stderr[:200]}")

print("🎬 All rounds processed.")


