"""
Module for detecting activities in video frames using a pre-trained model.

This module provides:
    - ActivityDetected: A class to represent a detected activity.
    - VideoActivityDetector: A class to process video frames, predict activities, annotate frames, and save analysis.
"""

import json
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from rich.pretty import pprint
from tqdm import tqdm

from video_analysis.logger import Logger
from video_analysis.util import write_text
from video_analysis.video import VideoCapture, VideoWriter


class ActivityDetected:
    """
    Represents a detected activity in a video frame.

    Attributes:
        activity (str): The name of the detected activity.
        confidence (float): The confidence score of the prediction.
        activity_id (int): The identifier of the predicted activity.
    """

    def __init__(self, activity: str, confidence: float, activity_id: int):
        """
        Initialize an ActivityDetected instance.

        Args:
            activity (str): The name of the detected activity.
            confidence (float): The confidence score, as a percentage.
            activity_id (int): The identifier for the activity.
        """
        self.activity = activity
        self.confidence = confidence
        self.activity_id = activity_id

    def __str__(self):
        """
        Return a string representation of the detected activity.
        """
        return f"Activity: {self.activity}, Confidence: {self.confidence:.2f}, Activity ID: {self.activity_id}"


class VideoActivityDetector:
    """
    Detects activities in video frames using a sliding window approach with a TensorFlow Hub model.

    Attributes:
        labels (list[str]): List of labels corresponding to the model's output.
        video (VideoCapture): Video source to read frames.
        output_video (VideoWriter): Video writer for annotated frames.
        output_analysis_csv (Path): File path for saving analysis in CSV format.
        output_analysis_json (Path): File path for saving analysis in JSON format.
        model: Loaded TensorFlow Hub model.
        window_size (int): Number of frames to consider in the sliding window.
        target_size (tuple): Target dimensions to which frames are resized.
        analysis (dict[int, list[ActivityDetected]]): Analysis results stored per frame.
    """

    def __init__(
        self,
        labels: list[str],
        input_video: VideoCapture,
        output_video: VideoWriter,
        output_analysis_csv: Path,
        output_analysis_json: Path,
        window_size: int = 50,
    ):
        """
        Initialize the VideoActivityDetector.

        Args:
            labels (list[str]): Activity labels.
            input_video (VideoCapture): Source video for processing.
            output_video (VideoWriter): Destination for annotated output video.
            output_analysis_csv (Path): Output CSV file path for analysis.
            output_analysis_json (Path): Output JSON file path for analysis.
            window_size (int): Size of the sliding window for activity detection.
        """
        self.labels = labels
        self.video = input_video
        self.output_video = output_video
        self.output_analysis_csv = output_analysis_csv
        self.output_analysis_json = output_analysis_json
        self.model = hub.load("https://tfhub.dev/tensorflow/movinet/a4/base/kinetics-600/classification/3")
        self.window_size = window_size  # Number of frames to consider in the sliding window
        self.target_size = (224, 224)  # Size to resize frames to
        self.analysis: dict[int, list[ActivityDetected]] = defaultdict(list)

    def prepare_frames(self, frames: list):
        """
        Prepare a list of frames for the TensorFlow model by resizing, converting color space, and normalizing.

        Args:
            frames (list): List of frames (numpy arrays).

        Returns:
            numpy.ndarray: Expanded dimensions array ready for prediction.
        """
        resized_frames = []
        for frame in frames:
            resized = cv2.resize(frame, self.target_size)
            resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            resized_frames.append(resized)

        frames_array = np.array(resized_frames)
        frames_array = frames_array / 255.0
        frames_array = frames_array.astype(np.float32)
        return np.expand_dims(frames_array, axis=0)

    def save_analysis_to_csv(self):
        """
        Save the activity analysis results to a CSV file.

        The CSV file includes frame IDs, activity names, confidence scores, and activity IDs.
        """
        with open(self.output_analysis_csv, "w") as f:
            f.write("Frame ID,Activity,Confidence,Activity ID\n")
            for frame_id, activities in self.analysis.items():
                for activity in activities:
                    f.write(f"{frame_id},{activity.activity},{activity.confidence:.2f},{activity.activity_id}\n")
        Logger.info(f"Analysis saved to {self.output_analysis_csv}")

    def save_analysis_to_json(self):
        """
        Save the summarized activity analysis to a JSON file and display counts.

        The JSON file maps activity names to the count of their occurrences.
        """
        counts = defaultdict(int)
        for activities in self.analysis.values():
            for activity in activities:
                counts[activity.activity] += 1
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        Logger.info("Activity analysis:")
        pprint(sorted_counts, indent_guides=False)
        with open(self.output_analysis_json, "w") as f:
            json.dump(counts, f, indent=4, sort_keys=True)
        Logger.info(f"Analysis saved to JSON file: {self.output_analysis_json}")

    def predict(self):
        """
        Process the video to predict activities for frames using a sliding window.

        Steps:
            1. Reads frames from the video source.
            2. Buffers frames until the window size is reached.
            3. Prepares frames and runs prediction via the TensorFlow model.
            4. Annotates each frame with the top 3 predicted activities.
            5. Writes the annotated frame to the output video.
            6. Saves analysis to CSV and JSON files after processing is completed.
        """
        frame_count = 0
        frames_buffer = []

        Logger.info("Starting video analysis...")
        Logger.info(f"Video dimensions: {self.video.width}x{self.video.height}, FPS: {self.video.fps}, Total frames: {self.video.total_frames}")
        Logger.info(f"Window size: {self.window_size}, Target size: {self.target_size}")
        Logger.info(f"Model loaded from: {self.model}")
        for chunk in tqdm(self.video.stream(), total=self.video.total_frames, desc="Processing frames"):
            # Append the current frame to the buffer
            frames_buffer.append(chunk.frame)
            frame_count += 1

            if len(frames_buffer) >= self.window_size:
                # Use the correct signature and input name
                frames = self.prepare_frames(frames_buffer)
                predictions = self.model.signatures["serving_default"](tf.constant(frames))
                # Extract the prediction tensor from the dictionary
                pred_tensor = next(iter(predictions.values()))
                # Now we can convert to numpy
                probs = pred_tensor.numpy()
                # Get top 3 predictions
                top_3_indices = np.argsort(probs[0])[-3:][::-1]

                first_frame = True
                for frame in frames_buffer:
                    y_pos = 30
                    current_frame = frame.copy()
                    for idx in top_3_indices:
                        activity = self.labels[idx] if idx < len(self.labels) else f"Activity_{idx}"
                        # confidence = probs[0][idx] * 10
                        confidence = probs[0][idx]
                        text = f"{activity}: {confidence:.2f}%"
                        write_text(current_frame, text, x=10, y=y_pos)
                        y_pos += 30
                        # save activity in analysis
                        if first_frame:
                            activity_detected = ActivityDetected(activity, confidence, idx)
                            self.analysis[frame_count].append(activity_detected)
                    first_frame = False

                    # Write frame to output video
                    self.output_video.write(current_frame)

                frames_buffer = []

        Logger.info("Video analysis completed.")
        self.save_analysis_to_csv()
        self.save_analysis_to_json()
        Logger.info("Video analysis saved to CSV/JSON and displayed.")
