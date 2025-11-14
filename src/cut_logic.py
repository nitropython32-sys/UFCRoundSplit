# import json
# import re
# import subprocess
# import os

# def clock_to_seconds(clock_str):
#     """Convert mm:ss or m.ss to seconds."""
#     clock_str = str(clock_str)
#     clock_str = clock_str.replace(".", ":")
#     parts = clock_str.split(":")
#     if len(parts) == 2:
#         return int(parts[0]) * 60 + float(parts[1])
#     return float(clock_str)


# def get_round(entry):
#     """Extract current round number."""
#     model = json.loads(entry["model_response"])
#     val = str(model.get("round", "")).strip()
#     m = re.search(r"(\d+)", val)
#     return int(m.group(1)) if m else None

# def get_clock(entry):
#     """Extract clock time (time left in round)."""
#     model = json.loads(entry["model_response"])
#     return clock_to_seconds(model.get("time", 0))


# # --- Load data ---
# with open("/home/nigel/Desktop/Projects/UFCRoundSplit/results.json", "r") as f:
#     data = json.load(f)

# body = data["results"]

# # --- Group by round ---
# rounds = {}
# for entry in body:
#     rnd = get_round(entry)
#     if rnd is None:
#         continue
#     rounds.setdefault(rnd, []).append(entry)


# results_summary = []

# tol = 2.0  # seconds tolerance

# for rnd, entries in rounds.items():
#     print(f"\n--- Round {rnd} ---")

#     for i in range(len(entries) - 1):
#         curr = entries[i]
#         nxt  = entries[i + 1]

#         curr_data = json.loads(curr["model_response"])
#         nxt_data  = json.loads(nxt["model_response"])

#         vt1, vt2 = map(clock_to_seconds, [curr["video_time"], nxt["video_time"]])
#         mt1, mt2 = map(clock_to_seconds, [curr_data["time"], nxt_data["time"]])

#         video_diff = vt2 - vt1
#         model_diff = mt1 - mt2

#         record = {
#             "round": rnd,
#             "index": i,
#             "video_diff": video_diff,
#             "model_diff": model_diff,
#             "status": None,
#             "note": ""
#         }

#         # direct match
#         if abs(video_diff - model_diff) < tol:
#             print(f"✅ Match: {video_diff:.2f}s ~ {model_diff:.2f}s")
#             record["status"] = "match"
#             record["note"] = "direct match"

#         # neighbor check
#         elif i + 2 < len(entries):
#             next_data = json.loads(entries[i + 2]["model_response"])
#             mt3 = clock_to_seconds(next_data["time"])
#             neighbor_diff = mt1 - mt3
#             if abs(video_diff - neighbor_diff) < tol:
#                 print(f"🟡 Adjusted match (offset 1): {video_diff:.2f}s ~ {neighbor_diff:.2f}s")
#                 record["status"] = "adjusted"
#                 record["note"] = "neighbor offset 1"
#                 record["neighbor_diff"] = neighbor_diff
#             else:
#                 print(f"⚠️ Edge case: video Δ={video_diff:.2f}s, model Δ={model_diff:.2f}s")
#                 record["status"] = "edge"
#                 record["note"] = "neighbor check failed"
#         else:
#             print(f"⚠️ Edge case: video Δ={video_diff:.2f}s, model Δ={model_diff:.2f}s")
#             record["status"] = "edge"
#             record["note"] = "no neighbor available"

#         results_summary.append(record)

# # # optional: print or save
# # for r in results_summary:
# #     print(r)

# ## optional: save to file
# # with open("results_summary.json", "w") as f:
# #     json.dump(results_summary, f, indent=2)



import json
import re
import os
import subprocess


############################################
#  TIME + ROUND UTILS
############################################

def clock_to_seconds(clock_str):
    """Convert mm:ss or m.ss to seconds."""
    if clock_str is None:
        return None
    clock_str = str(clock_str).replace(".", ":")
    parts = clock_str.split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(clock_str)


def get_round(entry):
    """Extract current round number from model_response JSON."""
    model = json.loads(entry["model_response"])
    val = str(model.get("round", "")).strip()
    m = re.search(r"(\d+)", val)
    return int(m.group(1)) if m else None


def get_clock(entry):
    """Extract mm:ss time-left from model_response."""
    model = json.loads(entry["model_response"])
    return clock_to_seconds(model.get("time", 0))


############################################
#  LOAD RESULTS
############################################

RESULTS_PATH = "/home/nigel/Desktop/Projects/UFCRoundSplit/results.json"

with open(RESULTS_PATH, "r") as f:
    data = json.load(f)

body = data["results"]


############################################
#  GROUP FRAMES BY ROUND
############################################

rounds = {}

for entry in body:
    rnd = get_round(entry)
    if rnd is None:
        continue
    rounds.setdefault(rnd, []).append(entry)


############################################
#  ROUND BOUNDARY DETECTION
############################################

round_boundaries = {}

for rnd, entries in rounds.items():
    clocks = []
    for e in entries:
        model = json.loads(e["model_response"])
        clock = clock_to_seconds(model.get("time"))
        video_t = clock_to_seconds(e["video_time"])
        if clock is None:
            continue
        clocks.append((clock, video_t))

    if not clocks:
        continue

    clocks.sort(key=lambda x: x[0])  # sort by model clock (time-left)

    earliest_clock, earliest_vid = clocks[0]
    latest_clock,   latest_vid   = clocks[-1]

    round_boundaries[rnd] = {
        "earliest_clock": earliest_clock,
        "earliest_video_time": earliest_vid,
        "latest_clock": latest_clock,
        "latest_video_time": latest_vid,
    }


############################################
#  EDGE CASE / INTERRUPTION DETECTION
############################################

tol = 2.0
results_summary = []
interruptions = []

for rnd, entries in rounds.items():

    for i in range(len(entries) - 1):
        curr = entries[i]
        nxt  = entries[i + 1]

        curr_data = json.loads(curr["model_response"])
        nxt_data  = json.loads(nxt["model_response"])

        vt1 = clock_to_seconds(curr["video_time"])
        vt2 = clock_to_seconds(nxt["video_time"])
        mt1 = clock_to_seconds(curr_data["time"])
        mt2 = clock_to_seconds(nxt_data["time"])

        if mt1 is None or mt2 is None:
            continue

        video_diff = vt2 - vt1
        model_diff = mt1 - mt2

        if abs(video_diff - model_diff) < tol:
            status = "match"
        else:
            status = "edge"
            interruptions.append({
                "round": rnd,
                "video_time": vt1,
                "next_video_time": vt2
            })

        results_summary.append({
            "round": rnd,
            "index": i,
            "video_diff": video_diff,
            "model_diff": model_diff,
            "status": status,
        })


############################################
#  BUILD CLEAN VIDEO SLICES PER ROUND
############################################

final_slices = {}

for rnd, bounds in round_boundaries.items():
    start = bounds["latest_video_time"]
    end   = bounds["earliest_video_time"]

    cuts = sorted([i["video_time"] for i in interruptions if i["round"] == rnd])

    slices = []
    current_start = start

    for cut in cuts:
        if current_start < cut < end:
            slices.append((current_start, cut))
            current_start = cut

    slices.append((current_start, end))

    slices = [s for s in slices if (s[1] - s[0]) > 1]  # remove <1 sec slices

    final_slices[rnd] = slices


############################################
#  SHOW RESULTS
############################################

print("\n==============================")
print("      ROUND CLEAN SLICES")
print("==============================\n")

for rnd, slices in final_slices.items():
    print(f"Round {rnd}:")
    for s in slices:
        print(f"   {s[0]:.2f}s  →  {s[1]:.2f}s")
    print()


############################################
#  FFMPEG CUTTER
############################################

def cut_rounds(input_path, cuts):
    """
    input_path: path to the full fight video
    cuts: list of dicts: { "round": N, "start_sec": float, "end_sec": float }
    """

    print("\n===================================")
    print("🎬 Starting ffmpeg Round Slicing...")
    print("===================================\n")

    for c in cuts:
        start = str(c["start_sec"])
        end = str(c["end_sec"])
        round_num = c["round"]

        output_path = f"round_{round_num}.mp4"
        print(f"⏱ Cutting Round {round_num}: {start}s → {end}s")

        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-ss", start,
            "-to", end,
            "-c", "copy",
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Saved {output_path}")
        else:
            print(f"⚠ Error cutting round {round_num}")
            print(result.stderr[:500])

    print("\n🎬 All rounds processed.\n")

############################################
#  PREPARE CUT DATA + RUN CUTTING
############################################

cuts = []
for rnd, segments in final_slices.items():
    for seg in segments:
        cuts.append({
            "round": rnd,
            "start_sec": seg[0],
            "end_sec": seg[1]
        })

# ➤ FIXED: Direct, correct path (NO replace!)
VIDEO_FILE = "/home/nigel/Desktop/Projects/UFCRoundSplit/Fights/YairRodriguezvsTheKoreanZombie.mp4"

print("VIDEO_FILE =", VIDEO_FILE)
print("Exists?", os.path.exists(VIDEO_FILE))
print("Is file?", os.path.isfile(VIDEO_FILE))

cut_rounds(VIDEO_FILE, cuts)










