from datetime import datetime
from pathlib import Path
from tempfile import gettempdir

from moviepy import VideoFileClip
from speech_recognition import AudioFile, Recognizer, RequestError, UnknownValueError
from transformers import pipeline

from video_analysis.logger import Logger

TEMP_DIR = Path(gettempdir())


class VideoSummarizationError(Exception):
    """
    Custom exception for errors related to video summarization.
    """

    pass


class AudioSummarization:
    """
    Class for summarizing audio content from a video file.

    Attributes:
        input_video (str): Path to the input video file.
        output_audio (str): Path to save the extracted audio file.
    """

    def __init__(self, input_video: str, output_folder: str):
        self.input_video = input_video
        self.output_folder = output_folder
        self._temp_audio = TEMP_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_audio.wav"
        self.summarizer = pipeline("summarization")

    def extract_audio(self):
        """
        Extract audio from the video file and save it to the specified path.
        """
        Logger.info("Extracting audio from video...")
        video = VideoFileClip(self.input_video)
        video.audio.write_audiofile(self._temp_audio, codec="pcm_s16le")
        video.close()
        Logger.info(f"Audio extracted to {self._temp_audio}")

    def save_text_to_file(self, text: str, filename: str):
        """
        Save the given text to a file.
        Args:
            text (str): The text to save.
            filename (str): The name of the file to save the text in.
        """
        output_file = Path(self.output_folder) / filename
        with open(output_file, "w") as f:
            f.write(text)
        Logger.info(f"Text saved to {output_file}")

    def transcribe_audio(self) -> str:
        """
        Read the extracted audio file and return its content.

        Returns:
            str: The content of the audio file.
        """
        Logger.info("Transcribing audio...")
        recognizer = Recognizer()
        with AudioFile(str(self._temp_audio)) as source:
            audio = recognizer.record(source)
        try:
            text: str = recognizer.recognize_google(audio, language="en-US")
            self.save_text_to_file(text, "transcribe.txt")
            Logger.info("Transcription successful.")
            return text
        except UnknownValueError:
            raise VideoSummarizationError("Google Speech Recognition could not understand the audio.")
        except RequestError as e:
            raise VideoSummarizationError(f"Could not request results from Google Speech Recognition service; {e}")
        finally:
            self._temp_audio.unlink(missing_ok=True)  # Remove the temporary audio file

    def summarize(self):
        """
        Main method to extract and transcribe audio from the video file.
        """
        self.extract_audio()
        transcription = self.transcribe_audio()
        Logger.info("Summarizing transcription...")
        summary = self.summarizer(transcription, max_length=150, min_length=30, do_sample=False)
        summary_text = summary[0]["summary_text"]
        self.save_text_to_file(summary_text, "summary.txt")
        Logger.info("Summarization complete.")

        Logger.info(f"Transcription saved to {self.output_folder}/transcribe.txt")
        Logger.info(f"Summary saved to {self.output_folder}/summary.txt")
