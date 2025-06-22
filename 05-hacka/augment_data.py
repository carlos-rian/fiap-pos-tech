"""
Dataset Augmentation Script for Pascal VOC Format

This script performs data augmentation on images with Pascal VOC XML annotations.
It applies various transformations (brightness/contrast, rotation, blur, noise, etc.)
to create multiple variations of each input image while preserving the bounding box
annotations.

Usage:
    1. Place your images and corresponding XML files in the INPUT_DIR folder
    2. Configure AUGMENTATIONS_PER_IMAGE to set how many variants to create
    3. Run the script to generate the augmented dataset in OUTPUT_DIR

Requirements:
    - albumentations
    - opencv-python
    - pathlib (standard library)
"""

import xml.etree.ElementTree as ET
from pathlib import Path

import albumentations as A
import cv2
import pandas

# --- CONFIGURATION ---
# 1. Place your images and XMLs exported from Label Studio in this folder
INPUT_DIR = Path("dataset_base_output")

# 2. Augmented images and XMLs will be saved here
OUTPUT_DIR = Path("dataset_base_augmented")

# 3. How many variants do you want to create PER ORIGINAL IMAGE?
# If you have 2 images and set 100 here, you'll have 200 images at the end.
AUGMENTATIONS_PER_IMAGE = 20
# --- END OF CONFIGURATION ---

RELEVANCE_FILTER = {"Medium", "Medium-High", "High"}

df = pandas.read_csv("dataset_base/mapping_images_with_relevance.csv")
IMAGES_WITH_RELEVANCE = set(df[df["RelevanceName"].isin(RELEVANCE_FILTER)]["ImageName"].tolist())


# Function to read Pascal VOC .xml files
def parse_voc_xml(xml_file: Path) -> tuple[list[list[int]], list[str]]:
    """
    Parse Pascal VOC XML annotation file to extract bounding boxes and labels.

    Args:
        xml_file: Path to the Pascal VOC XML annotation file.

    Returns:
        A tuple containing:
            - List of bounding boxes in format [xmin, ymin, xmax, ymax]
            - List of corresponding class labels

    Raises:
        ET.ParseError: If the XML file is malformed or cannot be parsed.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    bboxes = []
    labels = []
    for member in root.findall("object"):
        label = member.find("name").text
        xmin = int(member.find("bndbox").find("xmin").text)
        ymin = int(member.find("bndbox").find("ymin").text)
        xmax = int(member.find("bndbox").find("xmax").text)
        ymax = int(member.find("bndbox").find("ymax").text)
        bboxes.append([xmin, ymin, xmax, ymax])
        labels.append(label)
    return bboxes, labels


# Function to create a new Pascal VOC .xml file
def create_voc_xml(image_path: Path, bboxes: list[list[int]], labels: list[str], output_dir: Path) -> None:
    """
    Create a new Pascal VOC XML annotation file for an image.

    Args:
        image_path: Path to the image file.
        bboxes: List of bounding boxes in format [xmin, ymin, xmax, ymax].
        labels: List of class labels corresponding to each bounding box.
        output_dir: Directory where the XML file will be saved.

    Raises:
        cv2.error: If the image cannot be read or processed.
    """
    image_name = image_path.name
    height, width, _ = cv2.imread(str(image_path)).shape

    annotation = ET.Element("annotation")
    ET.SubElement(annotation, "folder").text = output_dir.name
    ET.SubElement(annotation, "filename").text = image_name
    ET.SubElement(annotation, "path").text = str(image_path)

    source = ET.SubElement(annotation, "source")
    ET.SubElement(source, "database").text = "Unknown"

    size = ET.SubElement(annotation, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    ET.SubElement(size, "depth").text = "3"

    ET.SubElement(annotation, "segmented").text = "0"

    for bbox, label in zip(bboxes, labels):
        obj = ET.SubElement(annotation, "object")
        ET.SubElement(obj, "name").text = label
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = "0"
        ET.SubElement(obj, "difficult").text = "0"
        bndbox = ET.SubElement(obj, "bndbox")
        ET.SubElement(bndbox, "xmin").text = str(int(bbox[0]))
        ET.SubElement(bndbox, "ymin").text = str(int(bbox[1]))
        ET.SubElement(bndbox, "xmax").text = str(int(bbox[2]))
        ET.SubElement(bndbox, "ymax").text = str(int(bbox[3]))

    tree = ET.ElementTree(annotation)
    xml_filename = image_path.stem + ".xml"
    tree.write(output_dir / xml_filename)


def clip_bboxes(bboxes: list[list[float]], image_height: int, image_width: int) -> list[list[int]]:
    """
    Clip bounding boxes to ensure they stay within image boundaries.

    Args:
        bboxes: List of bounding boxes in format [xmin, ymin, xmax, ymax]
        image_height: Height of the image
        image_width: Width of the image

    Returns:
        List of clipped bounding boxes as integers
    """
    clipped_bboxes = []
    for bbox in bboxes:
        xmin, ymin, xmax, ymax = bbox
        # Clip coordinates to image boundaries
        xmin = max(0, min(xmin, image_width - 1))
        ymin = max(0, min(ymin, image_height - 1))
        xmax = max(xmin + 1, min(xmax, image_width))
        ymax = max(ymin + 1, min(ymax, image_height))
        clipped_bboxes.append([int(xmin), int(ymin), int(xmax), int(ymax)])
    return clipped_bboxes


# Define augmentation pipeline. These are safe transformations for diagrams.
transform = A.Compose(
    [
        A.RandomBrightnessContrast(p=0.3),
        A.Affine(
            translate_percent={"x": (-0.03, 0.03), "y": (-0.03, 0.03)},
            scale=(0.95, 1.05),
            rotate=(-5, 5),
            p=0.7,
            border_mode=cv2.BORDER_CONSTANT,
            cval=(255, 255, 255),
        ),
        A.GaussianBlur(p=0.2),
        A.GaussNoise(p=0.2),
    ],
    bbox_params=A.BboxParams(format="pascal_voc", label_fields=["class_labels"]),
)


def process_images() -> None:
    """
    Process all images in the INPUT_DIR and create augmented versions.

    This function finds all image files in the input directory, processes each one
    with its corresponding XML annotation file, and generates augmented versions
    with updated bounding box coordinates.
    """
    # Create directories if they don't exist
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Place your images and XMLs in the folder: '{INPUT_DIR}' and run the script again.")

    # Find all image files with supported extensions
    image_files = []
    for file in INPUT_DIR.rglob("*"):
        if file.is_file() and file.suffix.lower() in {".png"} and file.parent.name in IMAGES_WITH_RELEVANCE:
            image_files.append(file)

    if not image_files:
        print(f"No images found in folder '{INPUT_DIR}'")
        return

    for image_file in image_files:
        xml_path = image_file.with_suffix(".xml")

        if not xml_path.exists():
            print(f"Warning: XML file not found for {image_file.name}. Skipping.")
            continue

        image = cv2.imread(str(image_file))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        bboxes, class_labels = parse_voc_xml(xml_path)

        print(f"Processing {image_file.name} and generating {AUGMENTATIONS_PER_IMAGE} variations...")

        for i in range(AUGMENTATIONS_PER_IMAGE):
            transformed = transform(image=image, bboxes=bboxes, class_labels=class_labels)

            transformed_image = transformed["image"]
            transformed_bboxes = transformed["bboxes"]
            transformed_labels = transformed["class_labels"]

            # Clip bounding boxes to image boundaries
            image_height, image_width, _ = transformed_image.shape
            transformed_bboxes = clip_bboxes(transformed_bboxes, image_height, image_width)

            # Preserve subfolder structure
            relative_path = image_file.relative_to(INPUT_DIR)
            output_subfolder = OUTPUT_DIR / relative_path.parent
            output_subfolder.mkdir(parents=True, exist_ok=True)

            # Generate a unique filename for the augmented image
            output_filename_base = f"{image_file.stem}_aug_{i}"
            output_image_path = output_subfolder / f"{output_filename_base}.png"

            # Save the augmented image
            cv2.imwrite(str(output_image_path), cv2.cvtColor(transformed_image, cv2.COLOR_RGB2BGR))

            # Create and save the corresponding XML
            create_voc_xml(output_image_path, transformed_bboxes, transformed_labels, output_subfolder)

    print("\nAugmentation process completed!")
    print(f"Your new dataset is ready in folder: '{OUTPUT_DIR}'")


if __name__ == "__main__":
    process_images()
