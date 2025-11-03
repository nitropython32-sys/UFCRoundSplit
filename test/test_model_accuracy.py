import pytest
import json
import os

# Change to your desired path
os.chdir("/home/nigel/Desktop/Projects/UFCRoundSplit/test/test_data")

# List all folders in the test set.
files = os.listdir()
# print(files)

for x in files:
    os.chdir(x)
    with open("results.json","r") as f:
        data = json.load(f)
    # print(data)
    data = data["results"]
    #so now we should have the results json file that allows me to iterate again
    for y in data:
        print(y)

    os.chdir("..")