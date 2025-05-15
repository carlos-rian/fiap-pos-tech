Link github: https://github.com/carlos-rian/fiap-pos-tech/tree/main/tech-challenge-04
Link video youtube: https://www.youtube.com/watch?v=k0YrGupHk9A

# Tech Challenge 04 - Video Analysis Application

## Description
This repository contains a video analysis application that performs activity detection and face/emotion recognition using TensorFlow and DeepFace. The application processes video files, annotates them with detected activities and emotions, and saves the results in various formats.

You must add the video "input_video.mp4" to the root directory of the project for the application to run successfully.

## Overview
This application provides comprehensive video analysis:
- **Activity Detection:** Implements a sliding window strategy with a TensorFlow Hub (Movinet) model to predict actions.
- **Face & Emotion Recognition:** Utilizes DeepFace and OpenCV to detect faces and determine the dominant emotion in each frame.
- **Audio Summarization:** Extracts and processes the audio track from the video to generate a concise summary of dialogues and audio events.

## Modules
- **main.py:** Entry point that configures file paths, output directories, and orchestrates the video analysis pipeline.
- **video_analysis/video.py:** Contains classes for video capture and writing.
- **video_analysis/activity_detector.py:** Handles batch processing of frames for activity detection, performing preprocessing, prediction, and annotation.
- **video_analysis/face_detector.py:** Performs face detection and emotion recognition, drawing bounding boxes and labels on detected faces.
- **video_analysis/logger.py:** Configures logging to output debug messages and track processing steps.
- **video_analysis/util.py:** Provides helper functions for tasks like rendering text with a background overlay.
- **video_analysis/kinetics_labels_600.txt:** Lists the activity labels corresponding to predictions from the TensorFlow model.
- **audio_analysis/audio_summarizer.py:** Extracts the audio track from the video and generates a concise summary of dialogues and key audio events.
- **pyproject.toml:** Manages project metadata and dependencies.
- **.gitignore & .python-version:** Specify files to ignore and enforce the Python version.

## Process
1. **Video Input & Capture:** 
   - Loads the video using OpenCV.
   - Processes the video frame by frame.
2. **Activity Detection:** 
   - Collects frames in a sliding window (50 frames).
   - Resizes, normalizes, and feeds frames into the TensorFlow model.
   - Extracts the top 3 predictions to annotate the video.
3. **Face & Emotion Analysis:** 
   - Applies DeepFace on each frame to detect faces and evaluate emotions.
   - Overlays bounding boxes and labels for the dominant emotion on detected faces.
4. **Output Generation:** 
   - Saves the annotated video files.
   - Generates detailed analysis reports in CSV, JSON, and JSONL formats within timestamped directories.
5. **Audio Summarization:** 
   - Extracts the audio track from the video.
   - Processes the audio to generate a concise summary of dialogues and key audio events.

## Setup & Installation
1. Ensure Python 3.12 is installed (see `.python-version`).
2. Install dependencies from `pyproject.toml`, for example using:
   ```bash
   uv sync --python 3.12
   ```
3. Run the application:
   ```bash
   uv run main.py
   ```

## Notes
- The activity detection uses a sliding window of 50 frames.
- Logging is configured for detailed debug output during processing.
- The generated output includes annotated videos along with analysis files in multiple formats.
