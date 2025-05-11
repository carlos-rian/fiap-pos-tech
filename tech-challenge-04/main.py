"""
Main execution module for the video analysis project.

This script orchestrates:
    - Activity detection in videos using a sliding window approach.
    - Face detection and emotion analysis using DeepFace.
    - Generation of output videos and analysis files in CSV, JSON, and JSONL formats.

Functions:
    video_activity_detector(...): Processes a video for activity detection.
    video_face_detector(...): Processes a video for face and emotion detection.
    main(): Sets up file paths and calls the detectors.
"""

from datetime import datetime
from pathlib import Path

import cv2
from deepface import DeepFace

from video_analysis.activity_detector import VideoActivityDetector
from video_analysis.audio_summarization import AudioSummarization
from video_analysis.face_detector import VideoFaceDetector, VideoFrame
from video_analysis.video import VideoCapture, VideoWriter

root_path = Path(__file__).parent


def video_activity_detector(
    label_file_path: Path, input_file: Path, output_file: Path, output_analysis_csv: Path, output_analysis_json: Path, window_size: int = 50
):
    """
    Detect activities in the video using a sliding window approach.

    This function initializes the video capture and writer, reads labels from the given file,
    instantiates a VideoActivityDetector, and processes the video to predict and annotate activity events.

    Args:
        label_file_path (Path): Path to the file containing activity labels.
        input_file (Path): Path to the input video file.
        output_file (Path): Path where the annotated output video will be saved.
        output_analysis_csv (Path): Path to save the CSV analysis result.
        output_analysis_json (Path): Path to save the JSON analysis result.
        window_size (int): Size of the sliding window for activity detection.
    """
    video_capture = VideoCapture(input_file)
    video_writer = VideoWriter(output_file, video_capture.width, video_capture.height, video_capture.fps)

    with open(label_file_path, "r") as f:
        labels = [line.strip() for line in f.readlines()]

    try:
        video_detector = VideoActivityDetector(
            labels, video_capture, video_writer, output_analysis_csv, output_analysis_json, window_size=window_size
        )
        video_detector.predict()
    finally:
        # Ensure resources are released even if an error occurs
        if video_capture.is_opened():
            video_capture.release()

        if video_writer.is_opened():
            video_writer.release()


def video_face_detector(input_file: Path, output_file: Path, output_analysis_jsonl: Path, output_analysis_json: Path):
    """
    Detect faces in the video and analyze emotions.

    This function defines an inner function 'analyze_frame' for processing each frame using DeepFace.
    It then initializes video capture and writer objects, and executes the face detector.

    Args:
        input_file (Path): Path to the input video file.
        output_file (Path): Path where the annotated output video will be saved.
        output_analysis_jsonl (Path): Path to save detailed analysis results in JSONL format.
        output_analysis_json (Path): Path to save summarized analysis results in JSON format.
    """

    def analyze_frame(frame: VideoFrame):
        """
        Analyze a single frame for face detection and emotion recognition.

        The frame is first converted to RGB format and then passed to DeepFace for face and emotion analysis.

        Args:
            frame (VideoFrame): The video frame to analyze.

        Returns:
            dict: Analysis results from DeepFace.
        """
        # Convert the frame to RGB format
        rgb_frame = cv2.cvtColor(frame.frame, cv2.COLOR_BGR2RGB)
        # Detect faces and emotions using DeepFace
        results = DeepFace.analyze(rgb_frame, actions=["emotion"], detector_backend="retinaface", enforce_detection=False, align=False)
        return results

    video_capture = VideoCapture(input_file)
    video_writer = VideoWriter(output_file, video_capture.width, video_capture.height, video_capture.fps)

    try:
        video_detector = VideoFaceDetector(analyze_frame, video_capture, video_writer, output_analysis_jsonl, output_analysis_json)
        video_detector.detect()
    finally:
        # Ensure resources are released even if an error occurs
        if video_capture.is_opened():
            video_capture.release()

        if video_writer.is_opened():
            video_writer.release()


def audio_summarization(input_video: str, output_folder: str):
    """
    Summarize the audio content of a video file.

    This function extracts audio from the video, transcribes it, and summarizes the transcription.

    Args:
        input_video (str): Path to the input video file.
        output_folder (str): Path to save the extracted audio and summary text files.
    """
    audio_summarizer = AudioSummarization(input_video, output_folder)
    audio_summarizer.summarize()


def main():
    """
    Main function to set up paths and start video processing.

    It defines:
      - The location of the input video.
      - Output directories and filenames (annotated video and analysis files).
      - Calls the face detector and activity detector functions with the proper arguments.
    """
    # video path
    video_path = root_path / "video"
    input_video = "input_video.mp4"

    # output folder (timestamped)
    folder = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_folder = video_path / "out" / folder
    output_folder.mkdir(parents=True, exist_ok=True)
    label_file_path = root_path / "video_analysis" / "kinetics_labels_600.txt"

    # output files for activity detector
    output_activity_detector_video = output_folder / "activity_detector.mp4"
    output_activity_detector_csv = output_folder / "activity_detector.csv"
    output_activity_detector_json = output_folder / "activity_detector.json"

    # output files for face detector
    output_face_detector_video = output_folder / "face_detector.mp4"
    output_face_detector_jsonl = output_folder / "face_detector.jsonl"
    output_face_detector_json = output_folder / "face_detector.json"

    # video face detector
    video_activity_detector(
        label_file_path=label_file_path,
        input_file=input_video,
        output_file=output_activity_detector_video,
        output_analysis_csv=output_activity_detector_csv,
        output_analysis_json=output_activity_detector_json,
        window_size=32,
    )
    # audio summarization
    audio_summarization(input_video, output_folder)

    # video activity detector
    video_face_detector(
        input_file=input_video,
        output_file=output_face_detector_video,
        output_analysis_jsonl=output_face_detector_jsonl,
        output_analysis_json=output_face_detector_json,
    )


if __name__ == "__main__":
    main()
