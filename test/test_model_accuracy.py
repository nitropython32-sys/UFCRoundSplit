import pytest
import json
import os
from generate_data import DataGenerator

###llm generated regex
import re

def regex_match_time(a, b):
    """Strict time comparison — must contain ':' and matching digits."""
    if a is None or b is None:
        return False
    a, b = str(a).strip(), str(b).strip()
    # reject if either one doesn't look like mm:ss
    if ":" not in a or ":" not in b:
        return False
    # normalize by removing spaces and leading zeros
    a = re.sub(r"\s+", "", a)
    b = re.sub(r"\s+", "", b)
    return a == b  # strict string match after cleanup


def regex_match_round(a, b):
    """Loose round comparison — allows '1', '1st', 'round 1', etc."""
    if a is None or b is None:
        return False
    a, b = str(a).lower().strip(), str(b).lower().strip()
    a = re.sub(r"[^a-z0-9]", "", a)
    b = re.sub(r"[^a-z0-9]", "", b)
    return bool(re.search(b, a)) or bool(re.search(a, b))



# Change to your desired path
os.chdir("/home/nigel/Desktop/Projects/UFCRoundSplit/test/test_data")

# List all folders in the test set.
files = os.listdir()
# print(files)

# test_model = DataGenerator("/home/nigel/Desktop/Projects/UFCRoundSplit/Fights","/home/nigel/Desktop/Projects/UFCRoundSplit/test/test_data")

for x in files:
    test_model = DataGenerator("/home/nigel/Desktop/Projects/UFCRoundSplit/Fights","/home/nigel/Desktop/Projects/UFCRoundSplit/test/test_data")

    ##for the test_model path.
    path = os.path.join("/home/nigel/Desktop/Projects/UFCRoundSplit/Fights", x)
    #lets load the model and gather the results to test on the dataset.
    result = test_model.get_video_results(path+".mp4")
    print(result)
    #ok now lets extract the values we want which is time and round
    test_data = result["results"]
    

    ###I am iteratively going through the local data set entries
    os.chdir(x)
    with open("results.json","r") as f:
        data = json.load(f)
    # print(data)
    data = data["results"]
    #so now we should have the results json file that allows me to iterate again
    for y in range(len(data)):
        model = data[y]["model_response"]
        test_model = test_data[y]["model_response"]
        try:
            model = json.loads(model)
            test_model = json.loads(test_model)
        except:
            print("json parse error")
            continue
        time = model.get("time")
        round = model.get("round")

        test_time = test_model.get("time")
        test_round = test_model.get("round")

        assert regex_match_time(time, test_time), f"time mismatch in {x} @ {y}: {time} != {test_time}"
        assert regex_match_round(round, test_round), f"round mismatch in {x} @ {y}: {round} != {test_round}"

    os.chdir("..")