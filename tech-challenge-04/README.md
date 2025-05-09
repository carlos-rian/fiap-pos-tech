# Tech Challenge 04 - Video Analysis Application

## Overview
This application analyzes videos to perform:
- **Activity Detection:** Uses a sliding window approach with a TensorFlow Hub (Movinet) model to predict activities.
- **Face & Emotion Detection:** Utilizes DeepFace and OpenCV to detect faces and analyze emotions in video frames.

## Modules
- **main.py:** Sets up file paths, output directories, and orchestrates the video processing pipeline.
- **video_analysis/video.py:** Provides classes for video capture and video writing.
- **video_analysis/activity_detector.py:** Implements activity detection by processing frames in batches and annotating them with prediction results.
- **video_analysis/face_detector.py:** Handles face detection and emotion analysis, drawing bounding boxes and labels.
- **video_analysis/logger.py:** Configures the logging for debugging and tracking.
- **video_analysis/util.py:** Contains helper functions such as writing text with a background for better readability.
- **video_analysis/kinetics_labels_600.txt:** Contains the activity labels used by the TensorFlow model.
- **pyproject.toml:** Manages project metadata and external dependencies.
- **.gitignore & .python-version:** Define files to ignore and the Python version to be used.

## Process
1. **Video Input & Capture:** Loads the video using OpenCV and processes it frame by frame.
2. **Activity Detection:** 
   - Frames are collected in a sliding window (50 frames).
   - Frames are resized, normalized, and fed to the TensorFlow model.
   - The top 3 predictions are extracted and annotated on the video.
3. **Face & Emotion Analysis:** 
   - Each frame is analyzed using DeepFace for face detection and emotion recognition.
   - Annotated with bounding boxes and labels based on the dominant emotion.
4. **Output:** 
   - Annotated videos are saved.
   - Detailed analysis outputs are generated in CSV, JSON, and JSONL formats.
   - Output folders are timestamped.

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
