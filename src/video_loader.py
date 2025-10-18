import ffmpeg

path = "/home/nigel/Desktop/Projects/UFCRoundSplit/Fights/UFC Classic： Yoel Romero vs Paulo Costa ｜ FULL FIGHT [mQCvriuwRDo].mp4"

info = ffmpeg.probe(path)
video_stream = next(s for s in info["streams"] if s["codec_type"] == "video")

width = int(video_stream["width"])
height = int(video_stream["height"])
fps_str = video_stream["r_frame_rate"]
num, den = map(int, fps_str.split("/"))
fps = num / den if den else 0

duration = float(info["format"]["duration"])

print(f"Resolution: {width}x{height}")
print(f"Frame rate: {fps:.2f} fps")
print(f"Duration: {duration:.2f} seconds")


###alright so now I know the frame rate and duration, lets just multiply and that will give me the total length
total_len = round(fps * duration)-1
print(total_len)

frame_num = round(total_len/2) # choose the frame index you want

out, _ = (
    ffmpeg
    .input("/home/nigel/Desktop/Projects/UFCRoundSplit/Fights/UFC Classic： Yoel Romero vs Paulo Costa ｜ FULL FIGHT [mQCvriuwRDo].mp4")
    .filter('select', f'gte(n,{frame_num})')
    .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
    .run(capture_stdout=True)
)

with open("frame_100.jpg", "wb") as f:
    f.write(out)

