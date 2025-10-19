import ffmpeg
import numpy as np

class Video:
    def __init__(self, path):
        self.path = path
        self.width = None
        self.height = None
        self.fps = None
        self.duration = None
        self.total_len = None
        self._load_info()  # auto-load metadata on creation

    def _load_info(self):
        """Get video metadata and store it in the instance."""
        info = ffmpeg.probe(self.path)
        video_stream = next(s for s in info["streams"] if s["codec_type"] == "video")

        self.width = int(video_stream["width"])
        self.height = int(video_stream["height"])
        fps_str = video_stream["r_frame_rate"]
        num, den = map(int, fps_str.split("/"))
        self.fps = num / den if den else 0
        self.duration = float(info["format"]["duration"])
        self.total_len = round(self.fps * self.duration) - 1

    def extract_frame(self, timestamp):
        """Extract a single frame at a given timestamp."""
        out, _ = (
            ffmpeg
            .input(self.path, ss=timestamp)
            .output('pipe:', vframes=1, format='rawvideo', pix_fmt='rgb24')
            .run(capture_stdout=True, quiet=True)
        )
        frame = np.frombuffer(out, np.uint8).reshape([self.height, self.width, 3])
        return frame

    @staticmethod
    def format_time(time):
        """Convert seconds to formatted time string."""
        hrs = int(time // 3600)
        mins = int((time % 3600) // 60)
        secs = int(time % 60)

        ret = ""
        if hrs > 0:
            ret += f"{hrs}:{mins:02d}:"
        else:
            ret += f"{mins}:{secs:02d}" if mins else f"0:{secs:02d}"
            return ret
        ret += f"{secs:02d}"
        return ret

    @staticmethod
    def get_frame_indices(total_frames, n):
        """Compute evenly distributed frame indices."""
        if n <= 0:
            return []

        indices = []
        queue = [(0, total_frames)]
        indices_set = set()

        while len(indices) < n and queue:
            start, end = queue.pop(0)
            mid = (start + end) // 2

            if mid not in indices_set:
                indices.append(mid)
                indices_set.add(mid)

            if len(indices) == n:
                break

            if start < mid:
                queue.append((start, mid))
            if mid + 1 < end:
                queue.append((mid + 1, end))

        return sorted(indices)

if __name__ == "__main__":
    pass
