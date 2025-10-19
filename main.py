# import moondream as md
# from PIL import Image
# from config import API_KEY

# # connect to Moondream Station
# # Initialize for Moondream Cloud
# model = md.vl(api_key=API_KEY)

# # Load an image
# image = Image.open("frame_135s.jpg")


# # Ask a question
# answer = model.query(image, """inside this image is a UFC fight, I need you to find the time clock. inside the time clock its should 
#                      the time of the round and what round `it is. rounds are between 1-3 or 1-5 depending on if its a championship fight or not.
#                      something to remember is sometimes you wont see a time clock at all and sometimes the fight the will be in between
#                      rounds as well. if thats the case return a null in json format else
#                      Return the time and rnd in json format""")["answer"]
# print("Answer:", answer)


import moondream as md
from PIL import Image
import json
from config import API_KEY
from src.video_loader import Video

# connect to Moondream Station
model = md.vl(api_key=API_KEY)

# load and sample video frames
v = Video("/home/nigel/Desktop/Projects/UFCRoundSplit/Fights/Yair Rodriguez vs The Korean Zombie Full Fight - EA Alter Egos： Prime Series 3 [W4-LEgjxokI].mp4")
indexes = Video.get_frame_indices(v.total_len, 8)
frames = [v.extract_frame(i / v.fps) for i in indexes]

# feed frames into model and collect captions
results = []
for frame in frames:
    img = Image.fromarray(frame)
    answer = model.query(img, """inside this image is a UFC fight, I need you to find the time clock. inside the time clock its should 
                     the time of the round and what round `it is. rounds are between 1-3 or 1-5 depending on if its a championship fight or not.
                     something to remember is sometimes you wont see a time clock at all and sometimes the fight the will be in between
                     rounds as well. if thats the case return a null in json format else
                     Return the time and rnd in json format""")["answer"]
    results.append(answer)

# save all 8 responses in one JSON file
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
