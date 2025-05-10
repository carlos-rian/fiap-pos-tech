"""
Logger configuration for the video_analysis module.

This module sets up and configures a dedicated logger for use throughout the project.
It specifies the logging format and debug level for debugging and informational purposes.
"""

import logging

Logger = logging.getLogger("video_analysis")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
Logger.setLevel(logging.INFO)
