import pytest
import json
import os
from generate_data import DataGenerator

# Change to your desired path
os.chdir("/home/nigel/Desktop/Projects/UFCRoundSplit/test/test_data")

# List all folders in the test set.
files = os.listdir()
# print(files)

test_model = DataGenerator("/home/nigel/Desktop/Projects/UFCRoundSplit/Fights","/home/nigel/Desktop/Projects/UFCRoundSplit/test/test_data")

for x in files:
    ##for the test_model path.
    path = os.path.join("/home/nigel/Desktop/Projects/UFCRoundSplit/Fights", x)
    #lets load the model and gather the results to test on the dataset.
    result = test_model.get_video_results(path+".mp4")
    print(result)
    #ok now lets extract the values we want which is time and round
    



    os.chdir(x)
    with open("results.json","r") as f:
        data = json.load(f)
    # print(data)
    data = data["results"]
    #so now we should have the results json file that allows me to iterate again
    for y in data:
        model = y["model_response"]
        try:
            model = json.loads(model)
        except:
            print("json parse error")
            continue
        time = model.get("time")
        round = model.get("round")
        print(time,round)
        
    os.chdir("..")