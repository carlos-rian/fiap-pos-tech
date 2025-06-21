import xml.etree.ElementTree as ET
from pathlib import Path

import albumentations as A
import cv2

# --- CONFIGURATION ---
# 1. Put your images and XMLs exported from Label Studio in this folder
INPUT_DIR = Path("dataset_base")

# 2. Augmented images and XMLs will be saved here
OUTPUT_DIR = Path("dataset_output")

# 3. How many variants do you want to create PER ORIGINAL IMAGE?
# If you have 2 images and set 100 here, you'll have 200 images in the end.
AUGMENTATIONS_PER_IMAGE = 20
# --- END CONFIGURATION ---


# Function to read Pascal VOC .xml files
def parse_voc_xml(xml_file: Path) -> tuple[list[list[int]], list[str]]:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    bboxes: list[list[int]] = []
    labels: list[str] = []
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
    image_name = Path(image_path).name
    height, width, _ = cv2.imread(str(image_path)).shape

    annotation = ET.Element("annotation")
    ET.SubElement(annotation, "folder").text = Path(output_dir).name
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
    xml_filename = Path(image_name).stem + ".xml"
    tree.write(Path(output_dir) / xml_filename)


# Define an augmentation pipeline. These are safe transformations for diagrams.
transform: A.Compose = A.Compose(
    [
        A.RandomBrightnessContrast(p=0.3),
        A.Rotate(limit=5, p=0.5, border_mode=cv2.BORDER_CONSTANT, value=255),
        A.GaussianBlur(p=0.2),
        A.GaussNoise(p=0.2),
        A.ShiftScaleRotate(
            shift_limit=0.06,
            scale_limit=0.1,
            rotate_limit=0,
            p=0.7,
            border_mode=cv2.BORDER_CONSTANT,
            value=255,
        ),
    ],
    bbox_params=A.BboxParams(format="pascal_voc", label_fields=["class_labels"]),
)


# Create directories if they don't exist
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

print(f"Put your images and XMLs in the folder: '{INPUT_DIR}' and run the script again.")

# Main loop
image_files: list[Path] = [f for f in INPUT_DIR.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg")]

for image_file in image_files:
    xml_file: Path = INPUT_DIR / f"{image_file.stem}.xml"

    if not xml_file.exists():
        print(f"Warning: XML file not found for {image_file.name}. Skipping.")
        continue

    image = cv2.imread(str(image_file))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    bboxes, class_labels = parse_voc_xml(xml_file)

    print(f"Processing {image_file.name} and generating {AUGMENTATIONS_PER_IMAGE} variations...")

    for i in range(AUGMENTATIONS_PER_IMAGE):
        transformed = transform(image=image, bboxes=bboxes, class_labels=class_labels)

        transformed_image = transformed["image"]
        transformed_bboxes = transformed["bboxes"]
        transformed_labels = transformed["class_labels"]

        # Generate a unique filename for the augmented image
        output_filename_base: str = f"{image_file.stem}_aug_{i}"
        output_image_path: Path = OUTPUT_DIR / f"{output_filename_base}.png"

        # Save the augmented image
        cv2.imwrite(str(output_image_path), cv2.cvtColor(transformed_image, cv2.COLOR_RGB2BGR))

        # Create and save the corresponding XML
        create_voc_xml(output_image_path, transformed_bboxes, transformed_labels, OUTPUT_DIR)

print("\nAugmentation process completed!")
print(f"Your new dataset is ready in the folder: '{OUTPUT_DIR}'")
