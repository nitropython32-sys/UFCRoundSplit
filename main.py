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
    
    answer = model.query(img, """You are a vision-language model. Examine the image carefully.

        Task:
        1. Determine if a UFC time clock is visible on screen.
        2. The clock normally shows both:
        - The time remaining in the round (e.g., "4:12", "2:07")
        - The round indicator (e.g., "1 of 3", "2 of 5", or a small group of white lines).
        3. If a time clock is visible:
        - Return a JSON object in this format:
            {"time": "<time_remaining>", "round": "<round_number_or_label>"}
        4. If **no clock** is visible (e.g., between rounds, replays, or ads):
        - Return exactly this JSON:
            {"time": null, "round": null}

        Rules:
        - You must NEVER guess values. If the clock is unclear, cropped, or partially hidden, treat it as missing.
        - Do not write explanations or extra text outside the JSON.
        - Your entire output must be **valid JSON only**.
        """)["answer"]

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
