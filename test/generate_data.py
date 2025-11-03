import moondream as md
from PIL import Image
import json
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import API_KEY
from src.video_loader import Video

class DataGenerator:
    def __init__(self, fights_dir, test_data_dir):
        self.fights_dir = fights_dir
        self.test_data_dir = test_data_dir
        self.model = md.vl(api_key=API_KEY)

    def get_video_results(self, video_path):
        v = Video(video_path)
        indexes = Video.get_frame_indices(v.total_len, 12)
        frames = [v.extract_frame(i / v.fps) for i in indexes]

        results = []
        for idx, i in enumerate(indexes):
            timestamp = i / v.fps
            img = Image.fromarray(frames[idx])
            
            answer = self.model.query(img, '''inside this image is a UFC fight, I need you to find the time clock. inside the time clock its should 
                            the time of the round and what round `it is. rounds are between 1-3 or 1-5 depending on if its a championship fight or not.
                            something to remember is sometimes you wont see a time clock at all and sometimes the fight the will be in between
                            rounds as well. if thats the case return a null in json format else
                            Return the time and rnd in json format''')["answer"]

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
        
        return output_data

    def generate(self):
        mp4_files = [f for f in os.listdir(self.fights_dir) if f.endswith('.mp4')]

        for video_filename in mp4_files:
            video_path = os.path.join(self.fights_dir, video_filename)
            video_name = os.path.splitext(video_filename)[0]
            output_dir = os.path.join(self.test_data_dir, video_name)
            os.makedirs(output_dir, exist_ok=True)

            v = Video(video_path)
            indexes = Video.get_frame_indices(v.total_len, 12)
            frames = [v.extract_frame(i / v.fps) for i in indexes]

            results = []
            for idx, i in enumerate(indexes):
                timestamp = i / v.fps
                img = Image.fromarray(frames[idx])
                
                # Save the frame as an image
                img.save(os.path.join(output_dir, f"{idx}.jpg"))

                answer = self.model.query(img, '''inside this image is a UFC fight, I need you to find the time clock. inside the time clock its should 
                                the time of the round and what round `it is. rounds are between 1-3 or 1-5 depending on if its a championship fight or not.
                                something to remember is sometimes you wont see a time clock at all and sometimes the fight the will be in between
                                rounds as well. if thats the case return a null in json format else
                                Return the time and rnd in json format''')["answer"]

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
            with open(os.path.join(output_dir, "results.json"), "w") as f:
                json.dump(output_data, f, indent=2)

if __name__ == "__main__":
    # FIGHTS_DIR = '/home/nigel/Desktop/Projects/UFCRoundSplit/Fights'
    # TEST_DATA_DIR = 'test_data'
    # generator = DataGenerator(FIGHTS_DIR, TEST_DATA_DIR)
    # generator.generate()
    pass