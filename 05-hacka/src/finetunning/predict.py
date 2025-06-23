import json
import random
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from time import sleep
from typing import Any

import cv2
import torch
import torchvision
from PIL import Image

from .util import PascalVOCDataset, get_model


def make_prediction(
    model: torch.nn.Module, image_path: Path, device: torch.device, confidence_threshold: float = 0.7
) -> tuple[list, list, list, int, int]:
    """
    Make a prediction on a single image.

    Args:
        model (torch.nn.Module): The trained PyTorch model.
        image_path (Path): Path to the input image.
        device (torch.device): Device to run the model on.
        confidence_threshold (float, optional): Minimum confidence score to keep a prediction. Defaults to 0.7.

    Returns:
        tuple[list, list, list, int, int]: Tuple containing predicted boxes, labels, scores, image width, and image height.
    """
    image = Image.open(image_path).convert("RGB")
    image_width, image_height = image.size
    transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])
    image_tensor = transform(image).to(device)
    model.eval()
    with torch.no_grad():
        prediction = model([image_tensor])
    pred_scores = prediction[0]["scores"].detach().cpu().numpy()
    pred_boxes = prediction[0]["boxes"].detach().cpu().numpy()[pred_scores >= confidence_threshold]
    pred_labels = prediction[0]["labels"].detach().cpu().numpy()[pred_scores >= confidence_threshold]
    pred_scores = pred_scores[pred_scores >= confidence_threshold]
    return pred_boxes, pred_labels, pred_scores, image_width, image_height


@lru_cache(maxsize=None)
def create_color(text: str) -> tuple:
    """
    Generate a random color for a given text label.

    Args:
        text (str): The label text.

    Returns:
        tuple: A tuple containing the box color (BGR) and font color (BGR).
    """
    random_color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )
    match random_color:
        case (r, g, b) if r + g + b > 650:
            t = f"{text}{random.randint(0, 10)}"
            color, _ = create_color(t)
        case _:
            color = random_color
    font_color = (255, 255, 255) if sum(color) < 500 else (0, 0, 0)
    return (color, font_color)


def draw_boxes_on_image(image_path: Path, boxes: list, labels: list, scores: list, class_map: dict, output_path: Path) -> None:
    """
    Draw bounding boxes and labels on the image and save the result.

    Args:
        image_path (Path): Path to the input image.
        boxes (list): List of bounding box coordinates.
        labels (list): List of label indices.
        scores (list): List of confidence scores.
        class_map (dict): Mapping from label indices to class names.
        output_path (Path): Path to save the annotated image.

    Returns:
        None
    """
    image = cv2.imread(str(image_path))
    colors = {}
    for label_int in class_map.keys():
        colors[label_int] = create_color(str(label_int))
    for i, box in enumerate(boxes):
        xmin, ymin, xmax, ymax = map(int, box)
        label_int = labels[i]
        class_name = class_map.get(label_int, "Desconhecido")
        score = scores[i]
        color, font_color = colors.get(label_int, ((255, 255, 255), (0, 0, 0)))
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
        text = f"{class_name}: {score:.2f}"
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(image, (xmin, ymin - text_height - 10), (xmin + text_width, ymin), color, -1)
        cv2.putText(image, text, (xmin, ymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, font_color, 2)
    cv2.imwrite(str(output_path), image)
    print(f"Image with predict save in: {output_path}")


def format_predictions_as_json(
    boxes: list, labels: list, scores: list, class_map: dict[int, str], image_width: int, image_height: int, model_path: Path
) -> dict[str, Any]:
    """
    Format PyTorch predictions as a dictionary similar to AutoML output.

    Args:
        boxes (list): List of bounding box coordinates.
        labels (list): List of label indices.
        scores (list): List of confidence scores.
        class_map (dict[int, str]): Mapping from label indices to class names.
        image_width (int): Width of the image.
        image_height (int): Height of the image.
        model_path (Path): Path to the trained model.

    Returns:
        dict[str, Any]: Dictionary containing formatted predictions and model info.
    """
    predictions_list = []
    for i, box in enumerate(boxes):
        xmin, ymin, xmax, ymax = box
        normalized_box = {
            "xMin": float(xmin / image_width),
            "yMin": float(ymin / image_height),
            "xMax": float(xmax / image_width),
            "yMax": float(ymax / image_height),
        }
        prediction_item = {"confidence": float(scores[i]), "displayName": class_map.get(labels[i], "Desconhecido"), "boundingBox": normalized_box}
        predictions_list.append(prediction_item)
    final_output = {"predictions": predictions_list, "modelInfo": {"type": "local_pytorch", "model_path": str(model_path)}}
    return final_output


def prepare_output_dirs(base_path: Path) -> tuple[Path, Path, Path]:
    """
    Create output directories and return the paths for the base, image, and JSON.

    Args:
        base_path (Path): Base directory for saving outputs.

    Returns:
        tuple[Path, Path, Path]: Tuple containing base output directory, image output path, and JSON output path.
    """
    datetime_now = datetime.now().strftime("%Y%m%d%H%M")
    base_output = Path(f"{base_path}/predictions/{datetime_now}")
    output_image_path = base_output / "prediction.png"
    output_json_path = base_output / "prediction.json"
    base_output.mkdir(parents=True, exist_ok=True)
    return base_output, output_image_path, output_json_path


def load_class_map(dataset_path: Path) -> tuple[dict[int, str], int]:
    """
    Load the class mapping from the PascalVOC dataset.

    Args:
        dataset_path (Path): Path to the PascalVOC dataset.

    Returns:
        tuple[dict[int, str], int]: Tuple containing class mapping and number of classes.
    """
    temp_dataset = PascalVOCDataset(root_dir=dataset_path)
    num_classes = len(temp_dataset.class_to_int) + 1
    class_map = temp_dataset.int_to_class
    return class_map, num_classes


def load_trained_model(model_path: Path, num_classes: int, device: torch.device) -> torch.nn.Module:
    """
    Load the trained model onto the specified device.

    Args:
        model_path (Path): Path to the trained model file.
        num_classes (int): Number of classes.
        device (torch.device): Device to load the model on.

    Returns:
        torch.nn.Module: The loaded model.
    """
    model = get_model(num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    return model


def save_json_output(json_output: dict, output_json_path: Path) -> None:
    """
    Save the prediction result in JSON format.

    Args:
        json_output (dict): Prediction results to save.
        output_json_path (Path): Path to save the JSON file.

    Returns:
        None
    """
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=4)
    print(f"✅ JSON output saved at: {output_json_path}")


def show_image_with_bounding_box(image_path: Path) -> None:
    """
    Display the annotated image (useful in notebooks).

    Args:
        image_path (Path): Path to the annotated image.

    Returns:
        None
    """
    result_image = cv2.imread(str(image_path))
    try:
        cv2.imshow("Image", result_image)
    except NameError:
        pass
    sleep(5)
    cv2.destroyAllWindows()


def run_prediction(
    image_path: Path, model_path: Path, dataset_path: Path, base_path: Path, save_json: bool = False, save_image: bool = False
) -> dict[str, Any]:
    """
    Run prediction on an image, optionally save the annotated image and JSON, and display the result.

    Args:
        image_path (Path): Path to the input image to be predicted.
        model_path (Path): Path to the trained model file.
        dataset_path (Path): Path to the dataset directory (for class mapping).
        base_path (Path): Base directory for saving outputs.
        save_json (bool, optional): If True, save the prediction results as a JSON file. Defaults to False.
        save_image (bool, optional): If True, save the annotated image with bounding boxes. Defaults to False.

    Returns:
        dict[str, Any]: Dictionary containing the prediction results in a format similar to AutoML output.
    """
    # Prepare output directories
    base_output, output_image_path, output_json_path = prepare_output_dirs(base_path)
    print(f"{model_path=}")
    print(f"{base_output=}")
    print(f"{output_image_path=}")
    print(f"{output_json_path=}")

    # Check if the image exists
    if not image_path.exists():
        print(f"❌ Error: Test image '{image_path}' not found.")
        print("Please update the image path.")
        return

    # Parameter configuration
    confidence = 0.7
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load class mapping
    print("Loading class mapping...")
    class_map, num_classes = load_class_map(dataset_path)

    # Load trained model
    print(f"Loading model from '{model_path}'...")
    model = load_trained_model(model_path, num_classes, device)

    # Prediction
    print(f"Making prediction on image '{image_path}'...")
    boxes, labels, scores, img_width, img_height = make_prediction(model, image_path, device, confidence)
    print(f"Found {len(boxes)} annotations. Drawing on image...")

    # Draw boxes and save results
    json_output = format_predictions_as_json(boxes, labels, scores, class_map, img_width, img_height, model_path)
    if save_image:
        print(f"Saving annotated image to '{output_image_path}'...")
        draw_boxes_on_image(image_path, boxes, labels, scores, class_map, output_image_path)
        show_image_with_bounding_box(output_image_path)
    if save_json:
        print(f"Saving JSON output to '{output_json_path}'...")
        save_json_output(json_output, output_json_path)

    return json_output
