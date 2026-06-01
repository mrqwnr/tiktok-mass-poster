import os
import random
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

class VideoEditor:
    """Handles video editing: trim, speed, text overlay."""

    def __init__(self, output_dir: str = "data/processed"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def process_video(self, input_path: str, caption_text: str, output_name: str = None) -> str:
        """
        Process a video:
        1. Random trim (keep 80-100% of original)
        2. Random speed (0.9x - 1.2x)
        3. Add text overlay
        Returns path to processed video.
        """
        clip = VideoFileClip(input_path)

        # Random trim
        duration = clip.duration
        trim_start = random.uniform(0, duration * 0.1)
        trim_end = random.uniform(duration * 0.9, duration)
        clip = clip.subclip(trim_start, trim_end)

        # Random speed
        speed = random.uniform(0.9, 1.2)
        clip = clip.fx(__import__("moviepy.video.fx.all", fromlist=["speedx"]).speedx, speed)

        # Add text overlay if caption provided
        if caption_text:
            txt_clip = (TextClip(
                caption_text,
                fontsize=40,
                color="white",
                stroke_color="black",
                stroke_width=2,
                font="Arial-Bold",
                method="caption",
                size=(clip.w - 40, None)
            )
            .set_position(("center", "bottom"))
            .set_duration(clip.duration)
            .margin(bottom=80, opacity=0))

            clip = CompositeVideoClip([clip, txt_clip])

        # Output
        if not output_name:
            output_name = f"processed_{random.randint(10000, 99999)}.mp4"
        output_path = os.path.join(self.output_dir, output_name)

        clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None
        )
        clip.close()
        return output_path

    def pick_random_video(self, video_paths: list) -> str:
        """Pick a random video from list."""
        return random.choice(video_paths)
