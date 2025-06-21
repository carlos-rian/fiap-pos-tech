"""
Dataset Generator for Object Detection

This module generates synthetic datasets for object detection by placing icons
on background images using a grid-based layout system. It includes data augmentation
techniques and generates Pascal VOC format annotations.

Author: Generated for FIAP Pos-Tech Hackathon
"""

import random
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Tuple
from xml.dom import minidom

from PIL import Image, ImageDraw, ImageEnhance
from tqdm import tqdm

# --- CONFIGURATION ---
BASE_DIR: Path = Path(__file__).parent
ICON_DIR: Path = BASE_DIR / "dataset_base/"
BACKGROUND_DIR: Path = BASE_DIR / "diagram_base/"
OUTPUT_DIR: Path = BASE_DIR / "dataset_output/"
ARTIFACTS_DIR: Path = OUTPUT_DIR / "artifacts/"

# Generation parameters
NUM_VARIATIONS_PER_ICON: int = 10
MIN_TOTAL_ICONS_PER_IMAGE: int = 4
MAX_TOTAL_ICONS_PER_IMAGE: int = 12

# NEW PARAMETER: Defines grid for distribution (rows, columns)
GRID_DIMENSIONS: Tuple[int, int] = (4, 5)  # 4 rows and 5 columns = 20 cells

# Augmentation parameters
ICON_SIZE_RANGE: Tuple = (64, 96, 128)  # Reduced to better fit in grid
ROTATION_RANGE: Tuple[float, float] = (-5.0, 5.0)
BRIGHTNESS_RANGE: Tuple[float, float] = (0.8, 1.2)
CONTRAST_RANGE: Tuple[float, float] = (0.8, 1.2)
# --- END CONFIGURATION ---

AnnotationObject = Dict[str, Any]


def get_asset_paths(directory: Path) -> List[Path]:
    """
    Recursively search for all image files in a directory.

    Args:
        directory (Path): Directory to search for image files

    Returns:
        List[Path]: List of paths to found image files
    """
    return list(directory.glob("**/*.png")) + list(directory.glob("**/*.jpg"))


def augment_icon(icon_image: Image.Image, max_size: Tuple[int, int]) -> Image.Image:
    """
    Apply augmentation to an icon image, ensuring it doesn't exceed the cell size.

    Args:
        icon_image (Image.Image): The original icon image
        max_size (Tuple[int, int]): Maximum size (width, height) the icon can have

    Returns:
        Image.Image: The augmented icon image
    """
    # Resize the icon to fit in the cell
    icon_image.thumbnail(max_size, Image.Resampling.LANCZOS)

    rotation_angle = random.uniform(*ROTATION_RANGE)
    icon_image = icon_image.rotate(rotation_angle, expand=True, resample=Image.Resampling.BICUBIC)

    enhancer = ImageEnhance.Brightness(icon_image)
    icon_image = enhancer.enhance(random.uniform(*BRIGHTNESS_RANGE))

    enhancer = ImageEnhance.Contrast(icon_image)
    icon_image = enhancer.enhance(random.uniform(*CONTRAST_RANGE))
    return icon_image


def generate_pascal_voc_xml(folder_name: str, image_filename: str, image_size: Tuple[int, int, int], objects: List[AnnotationObject]) -> str:
    """
    Generate a formatted XML string in Pascal VOC format.

    Args:
        folder_name (str): Name of the folder containing the image
        image_filename (str): Name of the image file
        image_size (Tuple[int, int, int]): Image dimensions (width, height, depth)
        objects (List[AnnotationObject]): List of annotation objects with labels and bounding boxes

    Returns:
        str: Pretty-formatted XML string in Pascal VOC format
    """
    annotation = ET.Element("annotation")
    ET.SubElement(annotation, "folder").text = folder_name
    ET.SubElement(annotation, "filename").text = image_filename
    size = ET.SubElement(annotation, "size")
    ET.SubElement(size, "width").text = str(image_size[0])
    ET.SubElement(size, "height").text = str(image_size[1])
    ET.SubElement(size, "depth").text = str(image_size[2])
    ET.SubElement(annotation, "segmented").text = "0"
    for obj in objects:
        ob = ET.SubElement(annotation, "object")
        ET.SubElement(ob, "name").text = obj["label"]
        ET.SubElement(ob, "pose").text = "Unspecified"
        ET.SubElement(ob, "truncated").text = "0"
        ET.SubElement(ob, "difficult").text = "0"
        bndbox = ET.SubElement(ob, "bndbox")
        ET.SubElement(bndbox, "xmin").text = str(obj["box"][0])
        ET.SubElement(bndbox, "ymin").text = str(obj["box"][1])
        ET.SubElement(bndbox, "xmax").text = str(obj["box"][2])
        ET.SubElement(bndbox, "ymax").text = str(obj["box"][3])
    xml_str = ET.tostring(annotation)
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent="  ")


def main() -> None:
    """
    Main function to orchestrate the dataset generation based on grid layout.

    This function:
    1. Sets up the output directory structure
    2. Loads icon and background images
    3. For each icon, generates multiple variations by:
       - Placing icons on a grid with random positions
       - Applying augmentations to individual icons
       - Saving images with Pascal VOC format annotations
    4. Creates artifact images with bounding box visualizations for debugging
    """
    print("--- Starting Dataset Generation (Grid Logic) ---")

    if OUTPUT_DIR.exists():
        print(f"Cleaning existing output directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    icon_paths = get_asset_paths(ICON_DIR)
    background_paths = get_asset_paths(BACKGROUND_DIR)

    if not icon_paths or not background_paths:
        print("Error: Check if 'dataset_base' and 'diagram_base' directories contain images.")
        return

    total_icons = len(icon_paths)
    print(f"Found {total_icons} icons and {len(background_paths)} backgrounds.")
    print("-" * 50)

    save_artifacts = True
    total_operations = total_icons * NUM_VARIATIONS_PER_ICON

    with tqdm(total=total_operations, desc="Generating dataset", unit="images") as pbar:
        for i, main_icon_path in enumerate(icon_paths):
            pbar.set_description(f"Processing {main_icon_path.stem} ({i + 1}/{total_icons})")
            other_icon_paths = [p for p in icon_paths if p != main_icon_path]

            for j in range(NUM_VARIATIONS_PER_ICON):
                bg_path = random.choice(background_paths)
                with Image.open(bg_path).convert("RGBA") as bg_image:
                    placed_annotations: List[AnnotationObject] = []

                    rows, cols = GRID_DIMENSIONS
                    cell_width = bg_image.width // cols
                    cell_height = bg_image.height // rows

                    grid_cells = [(r, c) for r in range(rows) for c in range(cols)]
                    random.shuffle(grid_cells)

                    num_total_icons = random.randint(MIN_TOTAL_ICONS_PER_IMAGE, MAX_TOTAL_ICONS_PER_IMAGE)

                    icons_to_place = [main_icon_path]
                    if other_icon_paths:
                        num_other_icons = min(num_total_icons - 1, len(other_icon_paths))
                        icons_to_place.extend(random.sample(other_icon_paths, num_other_icons))

                    for icon_path in icons_to_place:
                        if not grid_cells:
                            break  # No more grid cells available

                        row, col = grid_cells.pop()

                        with Image.open(icon_path).convert("RGBA") as icon_image:
                            # Passes the cell size to ensure the augmented icon fits
                            augmented_icon = augment_icon(icon_image.copy(), (cell_width, cell_height))

                            # Calculate position within the cell with jitter (variation)
                            cell_x_start = col * cell_width
                            cell_y_start = row * cell_height

                            # Free space within the cell for jitter
                            free_space_x = cell_width - augmented_icon.width
                            free_space_y = cell_height - augmented_icon.height

                            # Final icon position
                            paste_x = cell_x_start + random.randint(0, max(0, free_space_x))
                            paste_y = cell_y_start + random.randint(0, max(0, free_space_y))

                            bg_image.paste(augmented_icon, (paste_x, paste_y), augmented_icon)
                            placed_annotations.append(
                                {
                                    "label": icon_path.stem,
                                    "box": (paste_x, paste_y, paste_x + augmented_icon.width, paste_y + augmented_icon.height),
                                }
                            )

                    if any(ann["label"] == main_icon_path.stem for ann in placed_annotations):
                        output_subdir = OUTPUT_DIR / main_icon_path.parent.name / main_icon_path.stem
                        output_subdir.mkdir(parents=True, exist_ok=True)
                        base_filename = f"{main_icon_path.stem}_{j:04d}"
                        image_filename = f"{base_filename}{bg_path.suffix}"
                        final_image = bg_image.convert("RGB")
                        final_image.save(output_subdir / image_filename, "PNG")

                        xml_content = generate_pascal_voc_xml(
                            output_subdir.name, image_filename, (bg_image.width, bg_image.height, 3), placed_annotations
                        )
                        (output_subdir / f"{base_filename}.xml").write_text(xml_content, encoding="utf-8")

                        if save_artifacts:
                            # Save a copy of the final image and XML for debugging
                            artifact = ARTIFACTS_DIR / main_icon_path.name
                            # Drawing the image to visualize the bounding boxes

                            draw = ImageDraw.Draw(final_image)
                            for ann in placed_annotations:
                                box = ann["box"]
                                draw.rectangle(box, outline="red", width=2)
                                draw.text((box[0], box[1]), ann["label"], fill="white")
                            artifact.parent.mkdir(parents=True, exist_ok=True)
                            # Save draw image with bounding boxes
                            final_image.save(artifact, "PNG")
                            save_artifacts = False  # Save only once to avoid overhead

                # Update progress bar after each image is generated
                pbar.update(1)
                pbar.set_postfix({"Current": f"{main_icon_path.stem}_{j:04d}", "Icons": len(placed_annotations)})

            save_artifacts = True

    print("\n--- Dataset generation process completed! ---")


if __name__ == "__main__":
    main()
