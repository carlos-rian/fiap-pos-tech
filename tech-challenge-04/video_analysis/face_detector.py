"""
Module for detecting faces and analyzing emotions in video frames.

This module provides the VideoFaceDetector class which handles:
    - Face detection in each video frame using a provided detector callable.
    - Annotating frames with bounding boxes and dominant emotion labels.
    - Saving detailed analysis in JSONL and summarized results in JSON.

Usage:
    1. Create an instance of VideoFaceDetector with:
         • detector: A callable that returns detection results.
         • input_video: An object to capture video frames.
         • output_video: An object to write annotated video frames.
         • output_analysis_jsonl: Path to save detailed analysis.
         • output_analysis_json: Path to save summarized emotion counts.
    2. Call detect() to process the video and generate analysis.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Callable

import cv2
from pydantic import BaseModel
from tqdm import tqdm

from video_analysis.logger import Logger
from video_analysis.video import VideoCapture, VideoFrame, VideoWriter


class FrameAnalysed(BaseModel):
    """
    Data model representing the analysis details for a video frame.

    Attributes:
        frame_id (int): The identifier of the frame.
        region (tuple): The bounding box coordinates (x, y, w, h) of the detected face.
        dominate_emotion (str): The dominant emotion detected on the face.
        emotions (dict[str, float]): A mapping of emotion names to their corresponding scores.
    """

    frame_id: int
    region: tuple
    dominate_emotion: str
    emotions: dict[str, float] = {}


class VideoFaceDetector:
    """
    Class for detecting faces and annotating video frames with emotion analysis.

    Attributes:
        detector (Callable): Function used to detect faces and emotions in a frame.
        video (VideoCapture): Video source to read frames from.
        output_video (VideoWriter): Writer to output annotated video frames.
        output_analysis_jsonl (Path): Path to the JSONL file for detailed analysis.
        output_analysis_json (Path): Path to the JSON file for summarized analysis.
        analysis (dict[str, list[FrameAnalysed]]): Stores frame analysis categorized by dominant emotion.
    """

    def __init__(
        self, detector: Callable, input_video: VideoCapture, output_video: VideoWriter, output_analysis_jsonl: Path, output_analysis_json: Path
    ):
        """
        Initialize the VideoFaceDetector.

        Args:
            detector (Callable): A function that takes a VideoFrame and returns a list of detection results.
            input_video (VideoCapture): Video source for reading frames.
            output_video (VideoWriter): Destination for writing annotated frames.
            output_analysis_jsonl (Path): File path to save the detailed JSONL analysis.
            output_analysis_json (Path): File path to save the summarized JSON analysis.
        """
        self.detector = detector
        self.video = input_video
        self.output_video = output_video
        self.output_analysis_jsonl = output_analysis_jsonl
        self.output_analysis_json = output_analysis_json
        self.analysis: dict[str, list[FrameAnalysed]] = defaultdict(list)

    def save_analysis_to_jsonl(self):
        """
        Save the detailed analysis to a JSONL file, writing one JSON record per frame analyzed.
        """
        with open(self.output_analysis_jsonl, "w") as f:
            for _, frames in self.analysis.items():
                f.writelines([f"{frame.model_dump_json()}\n" for frame in frames])

        print(f"Analysis saved to JSONL file: {self.output_analysis_jsonl}")

    def save_analysis_to_json(self):
        """
        Save the summarized analysis to a JSON file, counting occurrences of each dominant emotion.
        """
        counts = defaultdict(int)
        for emotion, frames in self.analysis.items():
            counts[emotion] += len(frames)

        with open(self.output_analysis_json, "w") as f:
            json.dump(counts, f, indent=4, sort_keys=True)
        print(f"Analysis saved to JSON file: {self.output_analysis_json}")

    def get_color_by_emotion(self, emotion: str) -> tuple:
        """
        Get a color tuple based on the emotion string.

        Args:
            emotion (str): The emotion string.

        Returns:
            tuple: A tuple representing the color in BGR format.
        """
        colors = {
            "happy": (0, 255, 0),
            "sad": (255, 0, 0),
            "fear": (0, 255, 255),
            "angry": (0, 0, 255),
            "surprise": (255, 255, 0),
            "neutral": (255, 255, 255),
        }
        return colors.get(emotion.lower(), (255, 255, 255))

    def draw_bounding_boxes(self, frame: VideoFrame, results: list):
        """
        Draw bounding boxes around detected faces and annotate them with dominant emotion labels.

        Args:
            frame (VideoFrame): The video frame to annotate.
            results (list): A list of detection results with face regions and emotions.

        Returns:
            numpy.ndarray: The annotated frame with drawn bounding boxes and labels.
        """
        drawed_frame = frame.frame.copy()

        for face in results:
            if face["face_confidence"] < 0.3:
                continue

            dominate_emotion = face["dominant_emotion"]
            color = self.get_color_by_emotion(dominate_emotion)
            # get the bounding box of the face
            x, y, w, h = (face["region"]["x"], face["region"]["y"], face["region"]["w"], face["region"]["h"])
            # draw a rectangle around the face
            cv2.rectangle(drawed_frame, (x, y), (x + w, y + h), color, 3)
            # write the dominant emotion above the face
            cv2.putText(drawed_frame, dominate_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            # save the analysis
            self.analysis[dominate_emotion].append(
                FrameAnalysed(frame_id=frame.id, region=(x, y, w, h), dominate_emotion=dominate_emotion, emotions=face["emotion"])
            )

        return drawed_frame

    def detect(self):
        """
        Process the video frame by frame to detect faces, annotate frames, and save the analysis.

        It:
            1. Logs the start of analysis.
            2. Iterates through each frame using a progress bar.
            3. Applies the detector to process the frame.
            4. Annotates the frame with bounding boxes and labels.
            5. Writes the annotated frame to the output video.
            6. Saves detailed and summarized analysis results at the end.
        """
        Logger.info(f"Analyzing video: {self.video.video_path}")
        for frame in tqdm(self.video.stream(), total=self.video.total_frames, desc="Processing frames"):
            # Analyze the frame
            result = self.detector(frame)
            # Draw bounding boxes and emotions
            annotated_frame = self.draw_bounding_boxes(frame, result)
            # Write the annotated frame to the output video
            self.output_video.write(annotated_frame)

        Logger.info("Video analysis completed.")
        self.save_analysis_to_jsonl()
        self.save_analysis_to_json()
        Logger.info("Video analysis saved to JSON and displayed.")
