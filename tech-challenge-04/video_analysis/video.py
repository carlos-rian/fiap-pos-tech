from pathlib import Path

import cv2
from cv2.typing import MatLike


class VideoFrame:
    """
    Represents a single video frame.

    Attributes:
        id (int): Unique identifier for the frame.
        frame (MatLike): The image data for the frame.
    """

    def __init__(self, id: int, frame: MatLike):
        """
        Initialize a VideoFrame instance.

        Args:
            id (int): The unique frame identifier.
            frame (MatLike): The image data for this frame.
        """
        self.id = id
        self.frame = frame


class VideoCapture:
    """
    Handles video capture operations using OpenCV.

    Attributes:
        video_path (Path): The path to the video file.
        cap (cv2.VideoCapture): OpenCV video capture object.
    """

    def __init__(self, video_path: Path):
        """
        Initialize the video capture object.

        Args:
            video_path (Path): Path to the video file.

        Raises:
            ValueError: If the video file cannot be opened.
        """
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

    def is_opened(self):
        """
        Check if the video capture device is successfully opened.

        Returns:
            bool: True if the video capture is active, else False.
        """
        return self.cap.isOpened()

    @property
    def width(self):
        """
        Get the width of the video frames.

        Returns:
            int: Frame width in pixels.
        """
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        """
        Get the height of the video frames.

        Returns:
            int: Frame height in pixels.
        """
        return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def fps(self):
        """
        Get the frames per second (FPS) of the video.

        Returns:
            int: The video FPS.
        """
        return int(self.cap.get(cv2.CAP_PROP_FPS))

    @property
    def total_frames(self):
        """
        Get the total number of frames in the video.

        Returns:
            int: Total frame count.
        """
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def stream(self):
        """
        Generator that yields VideoFrame objects sequentially for each frame in the video.

        Yields:
            VideoFrame: The next video frame.
        """
        idx = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            yield VideoFrame(id=idx, frame=frame)
            idx += 1

    def release(self):
        """
        Release the video capture resource.
        """
        self.cap.release()


class VideoWriter:
    """
    Handles writing video frames to an output file using OpenCV.

    Attributes:
        output_path (Path): The file path for the output video.
        fourcc: Four-character code of codec used.
        out: OpenCV VideoWriter object.
    """

    def __init__(self, output_path: Path, width: int, height: int, fps: int):
        """
        Initialize the video writer with specified output settings.

        Args:
            output_path (Path): Path to the output video file.
            width (int): The width of the video frames.
            height (int): The height of the video frames.
            fps (int): Frames per second for the output video.
        """
        self.output_path = output_path
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.out = cv2.VideoWriter(str(output_path), self.fourcc, fps, (width, height), isColor=True)

    def write(self, frame: MatLike):
        """
        Write a single frame to the output video.

        Args:
            frame (MatLike): The video frame to write.
        """
        self.out.write(frame)

    def release(self):
        """
        Release the video writer resource.
        """
        self.out.release()
