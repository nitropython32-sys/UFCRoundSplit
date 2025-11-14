import json
from PIL import Image

from src.video_loader import Video
from src.model_logic import MoonModel


VIDEO_PATH = "/home/nigel/Desktop/Projects/UFCRoundSplit/Fights/YairRodriguezvsTheKoreanZombie.mp4"
OUTPUT_PATH = "results.json"
SAMPLE_RATE = 12  # frames per sample


def main():
    v = Video(VIDEO_PATH)

    # Frame indices and extracted frames
    frame_indices = Video.get_frame_indices(v.total_len, SAMPLE_RATE)
    frames = [v.extract_frame(idx / v.fps) for idx in frame_indices]

    results = []
    for idx, frame_idx in enumerate(frame_indices):
        timestamp = frame_idx / v.fps
        img = Image.fromarray(frames[idx])

        answer = MoonModel(img)

        results.append({
            "frame_index": frame_idx,
            "video_time": Video.format_time(timestamp),
            "raw_time_seconds": timestamp,
            "model_response": answer
        })

    header = {
        "length_of_video": Video.format_time(v.total_len / v.fps),
        "total_frames": v.total_len
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump({"header": header, "results": results}, f, indent=2)

    print(f"Saved results → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
