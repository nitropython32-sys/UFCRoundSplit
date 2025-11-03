import json
import os
import re
from generate_data import DataGenerator

def regex_match_time(a, b):
    if a is None or b is None:
        return False
    a, b = str(a).strip(), str(b).strip()
    if ":" not in a or ":" not in b:
        return False
    a = re.sub(r"\s+", "", a)
    b = re.sub(r"\s+", "", b)
    return a == b

def regex_match_round(a, b):
    if a is None or b is None:
        return False
    a, b = str(a).lower().strip(), str(b).lower().strip()
    a = re.sub(r"[^a-z0-9]", "", a)
    b = re.sub(r"[^a-z0-9]", "", b)
    return bool(re.search(b, a)) or bool(re.search(a, b))

# Change to your desired path
os.chdir("/home/nigel/Desktop/Projects/UFCRoundSplit/test/test_data")
files = os.listdir()

total_comparisons = 0
total_matches = 0

for x in files:
    print("\n==============================")
    print(f"▶ Processing: {x}")

    test_model = DataGenerator(
        "/home/nigel/Desktop/Projects/UFCRoundSplit/Fights",
        "/home/nigel/Desktop/Projects/UFCRoundSplit/test/test_data"
    )

    path = os.path.join("/home/nigel/Desktop/Projects/UFCRoundSplit/Fights", x)
    result = test_model.get_video_results(path + ".mp4")
    test_data = result["results"]

    os.chdir(x)
    with open("results.json", "r") as f:
        data = json.load(f)["results"]

    for y in range(len(data)):
        try:
            model = json.loads(data[y]["model_response"])
            test_entry = json.loads(test_data[y]["model_response"])
        except:
            print(f"⚠️ json parse error in {x} index {y}")
            continue

        time = model.get("time")
        round = model.get("round")
        test_time = test_entry.get("time")
        test_round = test_entry.get("round")

        # ---- Comparison ----
        time_match = regex_match_time(time, test_time)
        round_match = regex_match_round(round, test_round)
        total_comparisons += 2  # time + round

        if time_match:
            total_matches += 1
            print(f"✅ time match in {x} @ {y}: {time} == {test_time}")
        else:
            print(f"❌ time mismatch in {x} @ {y}: {time} != {test_time}")

        if round_match:
            total_matches += 1
            print(f"✅ round match in {x} @ {y}: {round} == {test_round}")
        else:
            print(f"❌ round mismatch in {x} @ {y}: {round} != {test_round}")

    os.chdir("..")

# ---- Summary ----
print("\n==============================")
accuracy = (total_matches / total_comparisons * 100) if total_comparisons else 0
print(f"✅ Total comparisons: {total_comparisons}")
print(f"✅ Total matches: {total_matches}")
print(f"📊 Accuracy: {accuracy:.2f}%")
