import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import torch
import torchvision
import torchvision.transforms as T
from PIL import Image
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor


class PascalVOCDataset(torch.utils.data.Dataset):
    """
    PyTorch Dataset for Pascal VOC-style datasets with PNG images and XML annotations.
    """

    def __init__(self, root_dir: Path, transforms=None):
        self.root_dir = root_dir
        self.transforms = transforms
        self.image_paths = sorted([p for p in root_dir.glob("*.png") if (p.with_suffix(".xml")).exists()])
        all_labels = self._find_all_unique_labels()
        self.class_to_int = {label: i + 1 for i, label in enumerate(all_labels)}
        self.int_to_class = {i: label for label, i in self.class_to_int.items()}

    def _find_all_unique_labels(self) -> list[str]:
        """
        Find all unique class labels in the dataset.
        """
        unique_labels = set()
        for img_path in self.image_paths:
            xml_path = img_path.with_suffix(".xml")
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for member in root.findall("object"):
                unique_labels.add(member.find("name").text)
        return sorted(list(unique_labels))

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, dict[str, Any]]:
        image_path = self.image_paths[idx]
        xml_path = image_path.with_suffix(".xml")
        image = Image.open(image_path).convert("RGB")
        tree = ET.parse(xml_path)
        root = tree.getroot()
        boxes = []
        labels = []
        for member in root.findall("object"):
            xmin = int(member.find("bndbox").find("xmin").text)
            ymin = int(member.find("bndbox").find("ymin").text)
            xmax = int(member.find("bndbox").find("xmax").text)
            ymax = int(member.find("bndbox").find("ymax").text)
            boxes.append([xmin, ymin, xmax, ymax])
            class_name = member.find("name").text
            labels.append(self.class_to_int[class_name])
        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        labels = torch.as_tensor(labels, dtype=torch.int64)
        image_id = torch.tensor([idx])
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        iscrowd = torch.zeros((len(boxes),), dtype=torch.int64)
        target = {"boxes": boxes, "labels": labels, "image_id": image_id, "area": area, "iscrowd": iscrowd}
        if self.transforms:
            image = self.transforms(image)
        return image, target

    def __len__(self) -> int:
        return len(self.image_paths)


def get_transform() -> T.Compose:
    """
    Returns the torchvision transform to convert images to tensors.
    """
    return T.Compose([T.ToTensor()])


def get_model(num_classes: int) -> torchvision.models.detection.FasterRCNN:
    """
    Returns a Faster R-CNN model with the specified number of classes.
    """
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights="DEFAULT")
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    return model


def get_class_from_prediction(prediction: dict[str, list[dict[str, str | float]]]) -> set[str]:
    """
    Extracts the class name from a prediction dictionary.

    Args:
        prediction: A dictionary containing the prediction results.

    Returns:
        The class name as a string.
    """
    """
    {"predictions": [
        {
            "confidence": 0.9979641437530518,
            "displayName": "microsoft_entra",
            "boundingBox": {
                "xMin": 0.32125431299209595,
                "yMin": 0.3538549244403839,
                "xMax": 0.4012775421142578,
                "yMax": 0.4597073495388031
            }
        }
    ]}
    """
    class_names = [pred.get("displayName") for pred in prediction.get("predictions", [])]
    return set(class_names)
