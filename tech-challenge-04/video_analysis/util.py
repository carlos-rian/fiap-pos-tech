"""
Utility functions for video analysis.

This module provides helper functions such as write_text, which draws text with a background rectangle on a frame for better readability.
"""

import cv2


def write_text(frame, text, x=10, y=30):
    """
    Write text on a frame with a background rectangle for improved visibility.

    Args:
        frame: The image frame (numpy array) where the text will be drawn.
        text (str): The string to be displayed on the frame.
        x (int, optional): The x-coordinate for the text placement. Defaults to 10.
        y (int, optional): The y-coordinate for the text placement. Defaults to 30.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_color = (255, 255, 255)
    line_type = 2

    # Get the text size
    text_size = cv2.getTextSize(text, font, font_scale, line_type)[0]

    # Set the rectangle coordinates
    x, y = x, y
    rect_start = (x - 5, y - text_size[1] - 5)
    rect_end = (x + text_size[0] + 5, y + 5)

    # Draw the rectangle and the text
    cv2.rectangle(frame, rect_start, rect_end, (0, 0, 0), -1)
    cv2.putText(frame, text, (x, y), font, font_scale, font_color, line_type)
