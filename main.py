import moondream as md
from PIL import Image
import json
from config import API_KEY
from src.video_loader import Video

# connect to Moondream Station
model = md.vl(api_key=API_KEY)

# load and sample video frames
v = Video("/home/nigel/Desktop/Projects/UFCRoundSplit/Fights/Yair Rodriguez vs The Korean Zombie Full Fight - EA Alter Egos： Prime Series 3 [W4-LEgjxokI].mp4")
indexes = Video.get_frame_indices(v.total_len, 20)
frames = [v.extract_frame(i / v.fps) for i in indexes]

results = []
for i in indexes:
    timestamp = i / v.fps
    img = Image.fromarray(frames[indexes.index(i)])
    
    answer = model.query(img, """inside this image is a UFC fight, I need you to find the time clock. inside the time clock its should 
                     the time of the round and what round `it is. rounds are between 1-3 or 1-5 depending on if its a championship fight or not.
                     something to remember is sometimes you wont see a time clock at all and sometimes the fight the will be in between
                     rounds as well. if thats the case return a null in json format else
                     Return the time and rnd in json format""")["answer"]

    results.append({
        "frame_index": i,
        "video_time": Video.format_time(timestamp),
        "raw_time_seconds": timestamp,
        "model_response": answer
    })


# Create the header
header = {
    "length_of_video": Video.format_time(v.total_len / v.fps),
    "total_frames": v.total_len
}

# Combine header and results
output_data = {
    "header": header,
    "results": results
}

# save all responses in one JSON file
with open("results.json", "w") as f:
    json.dump(output_data, f, indent=2)
