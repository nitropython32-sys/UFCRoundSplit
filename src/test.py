# import re
# import json

# def get_round_entries(body, round_number):
#     pattern = r"(\d+)"  # capture first number (handles "1" or "1 of 5")
#     results = []

#     for entry in body:
#         model = json.loads(entry["model_response"])
#         round_val = str(model.get("round", "")).strip()

#         match = re.search(pattern, round_val)
#         if match and int(match.group(1)) == round_number:
#             results.append(entry)
#     return results

# # Open and load a JSON file
# with open("/home/nigel/Desktop/Projects/UFCRoundSplit/results.json", "r") as f:
#     data = json.load(f)

# print(data)

# header = data["header"]
# body = data["results"]

# for x in range(1,6):
#     rnd = get_round_entries(body,x)

import json
import re

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

















# def rnd_data(text):
#     pattern = r"(\d+)(?:\s*of\s*(\d+))?"

#     match = re.search(pattern, text)
#     if match:
#         current = int(match.group(1))
#         total = int(match.group(2)) if match.group(2) else None
#         # print(current, total)
#     return int(current)
##so we need to extract all the rounds we have
# rnd = set()
# for x in range(len(body)):
#     test = json.loads(body[x]["model_response"])
#     try:
#         rnd.add(int(test["round"]))
#     except:
#         rnd.add(rnd_data(test["round"]))
