import json
import re
import subprocess
import os


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


# ##so here each round has its entries in order
# for rnd, entries in rounds.items():
#     for entry in entries:
#         time = entry.get("video_time")
#         model_response = entry.get("model_response")

#         if model_response:
#             data = json.loads(model_response)
#             model_time = data.get("time")
#         else:
#             model_time = None

#         print(rnd, time, model_time)



import json

def clock_to_seconds(clock_str):
    """Convert mm:ss or m.ss to seconds."""
    clock_str = str(clock_str)
    clock_str = clock_str.replace(".", ":")
    parts = clock_str.split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(clock_str)


tol = 2.0  # seconds tolerance

for rnd, entries in rounds.items():
    print(f"\n--- Round {rnd} ---")

    for i in range(len(entries) - 1):
        curr = entries[i]
        nxt  = entries[i + 1]

        curr_data = json.loads(curr["model_response"])
        nxt_data  = json.loads(nxt["model_response"])

        vt1, vt2 = map(clock_to_seconds, [curr["video_time"], nxt["video_time"]])
        mt1, mt2 = map(clock_to_seconds, [curr_data["time"], nxt_data["time"]])

        video_diff = vt2 - vt1
        model_diff = mt1 - mt2

        # direct match
        if abs(video_diff - model_diff) < tol:
            print(f"✅ Match: {video_diff:.2f}s ~ {model_diff:.2f}s")
            continue

        # neighbor check (off-by-one compensation)
        if i + 2 < len(entries):
            next_data = json.loads(entries[i + 2]["model_response"])
            mt3 = clock_to_seconds(next_data["time"])
            neighbor_diff = mt1 - mt3
            if abs(video_diff - neighbor_diff) < tol:
                print(f"🟡 Adjusted match (offset 1): {video_diff:.2f}s ~ {neighbor_diff:.2f}s")
                continue

        print(f"⚠️ Edge case: video Δ={video_diff:.2f}s, model Δ={model_diff:.2f}s")















