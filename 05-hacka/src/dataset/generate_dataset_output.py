"""
Dataset Generator for Object Detection

This module generates synthetic datasets for object detection by placing icons
on background images using a grid-based layout system. It includes data augmentation
techniques and generates Pascal VOC format annotations.

Author: Generated for FIAP Pos-Tech Hackathon
"""

import multiprocessing as mp
import random
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from xml.dom import minidom

import pandas
from PIL import Image, ImageEnhance
from tqdm import tqdm

# --- CONFIGURATION ---
BASE_DIR: Path = Path(__file__).parent
ICON_DIR: Path = BASE_DIR / "dataset_base/"
BACKGROUND_DIR: Path = BASE_DIR / "diagram_base/"
OUTPUT_DIR: Path = BASE_DIR / "dataset_output/"

# Generation parameters
NUM_VARIATIONS_PER_ICON: int = 5
MIN_TOTAL_ICONS_PER_IMAGE: int = 6
MAX_TOTAL_ICONS_PER_IMAGE: int = 14
NUM_WORKERS: int = mp.cpu_count() - 1  # Leave one CPU core free

# NEW PARAMETER: Defines grid for distribution (rows, columns)
GRID_DIMENSIONS: tuple[int, int] = (4, 5)  # 4 rows and 5 columns = 20 cells

# Augmentation parameters
ICON_SIZE_RANGE: tuple = (64, 96, 128)  # Reduced to better fit in grid
ROTATION_RANGE: tuple[float, float] = (-5.0, 5.0)
BRIGHTNESS_RANGE: tuple[float, float] = (0.8, 1.2)
CONTRAST_RANGE: tuple[float, float] = (0.8, 1.2)


RELEVANCE_FILTER = {"High"}

df = pandas.read_csv(BASE_DIR / "dataset_base/mapping_images_with_relevance.csv")
IMAGES_WITH_RELEVANCE = set(df[df["RelevanceName"].isin(RELEVANCE_FILTER)]["ImageName"].tolist())


# --- END CONFIGURATION ---

AnnotationObject = dict[str, Any]


def get_asset_paths(directory: Path) -> list[Path]:
    """
    Recursively search for all image files in a directory.

    Args:
        directory (Path): Directory to search for image files

    Returns:
        List[Path]: List of paths to found image files
    """
    return list(directory.glob("**/*.png")) + list(directory.glob("**/*.jpg"))


def filter_images_with_relevance(directory: Path) -> list[Path]:
    return [img for img in get_asset_paths(directory) if img.is_file() and img.stem in IMAGES_WITH_RELEVANCE]


def augment_icon(icon_image: Image.Image, max_size: tuple[int, int]) -> Image.Image:
    """
    Apply augmentation to an icon image, ensuring it doesn't exceed the cell size.

    Args:
        icon_image (Image.Image): The original icon image
        max_size (Tuple[int, int]): Maximum size (width, height) the icon can have

    Returns:
        Image.Image: The augmented icon image
    """
    icon_side = random.choice(ICON_SIZE_RANGE)
    icon_image = icon_image.copy()
    icon_image.thumbnail((icon_side, icon_side), Image.Resampling.LANCZOS)

    rotation_angle = random.uniform(*ROTATION_RANGE)
    icon_image = icon_image.rotate(rotation_angle, expand=True, resample=Image.Resampling.BICUBIC)

    enhancer = ImageEnhance.Brightness(icon_image)
    icon_image = enhancer.enhance(random.uniform(*BRIGHTNESS_RANGE))

    enhancer = ImageEnhance.Contrast(icon_image)
    icon_image = enhancer.enhance(random.uniform(*CONTRAST_RANGE))
    return icon_image


def generate_pascal_voc_xml(
    folder_name: str,
    image_filename: str,
    image_size: tuple[int, int, int],
    objects: list[AnnotationObject],
) -> str:
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


def generate_single_variation(task_data: dict[str, Any]) -> dict[str, Any]:
    """
    Generate a single image variation - designed for parallel processing.

    Args:
        task_data (Dict[str, Any]): Dictionary containing all necessary data for generation

    Returns:
        Dict[str, Any]: Result dictionary with success status and metadata
    """
    try:
        main_icon_path = Path(task_data["main_icon_path"])
        variation_index = task_data["variation_index"]
        bg_path = Path(task_data["bg_path"])
        other_icon_paths = [Path(p) for p in task_data["other_icon_paths"]]
        output_subdir = Path(task_data["output_subdir"])

        # Ensure output directory exists
        output_subdir.mkdir(parents=True, exist_ok=True)

        with Image.open(bg_path).convert("RGBA") as bg_image:
            placed_annotations: list[AnnotationObject] = []

            rows, cols = GRID_DIMENSIONS
            # Safe zone: 10% de margem em todos os lados
            margin_x = int(bg_image.width * 0.10)
            margin_y = int(bg_image.height * 0.10)
            safe_width = bg_image.width - 2 * margin_x
            safe_height = bg_image.height - 2 * margin_y
            cell_width = safe_width // cols
            cell_height = safe_height // rows

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

                    # Posição da célula dentro da safe zone
                    cell_x_start = margin_x + col * cell_width
                    cell_y_start = margin_y + row * cell_height

                    # Espaço livre dentro da célula
                    free_space_x = cell_width - augmented_icon.width
                    free_space_y = cell_height - augmented_icon.height

                    # Posição final do ícone dentro da célula
                    paste_x = cell_x_start + random.randint(0, max(0, free_space_x))
                    paste_y = cell_y_start + random.randint(0, max(0, free_space_y))

                    bg_image.paste(augmented_icon, (paste_x, paste_y), augmented_icon)
                    placed_annotations.append(
                        {
                            "label": icon_path.stem,
                            "box": (paste_x, paste_y, paste_x + augmented_icon.width, paste_y + augmented_icon.height),
                        }
                    )

            # Only save if the main icon is present
            if any(ann["label"] == main_icon_path.stem for ann in placed_annotations):
                base_filename = f"{main_icon_path.stem}_{variation_index:04d}"
                image_filename = f"{base_filename}{bg_path.suffix}"
                final_image = bg_image.convert("RGB")
                final_image.save(output_subdir / image_filename, "PNG")

                xml_content = generate_pascal_voc_xml(output_subdir.name, image_filename, (bg_image.width, bg_image.height, 3), placed_annotations)
                (output_subdir / f"{base_filename}.xml").write_text(xml_content, encoding="utf-8")

                return {
                    "success": True,
                    "main_icon": main_icon_path.stem,
                    "variation": variation_index,
                    "icons_placed": len(placed_annotations),
                    "image_filename": image_filename,
                }
            else:
                return {"success": False, "main_icon": main_icon_path.stem, "variation": variation_index, "reason": "Main icon not placed"}

    except Exception as e:
        return {
            "success": False,
            "main_icon": task_data.get("main_icon_path", "unknown"),
            "variation": task_data.get("variation_index", -1),
            "error": str(e),
        }


def main() -> None:
    """
    Main function to orchestrate the parallel dataset generation.

    This function:
    1. Sets up the output directory structure
    2. Loads icon and background images
    3. Creates tasks for parallel processing
    4. Uses multiprocessing to generate image variations in parallel
    5. Creates artifact images with bounding box visualizations for debugging
    """
    print("--- Starting Dataset Generation (Parallel Processing) ---")
    print(f"Using {NUM_WORKERS} worker processes")

    if OUTPUT_DIR.exists():
        print(f"Cleaning existing output directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    icon_paths = filter_images_with_relevance(ICON_DIR)
    background_paths = get_asset_paths(BACKGROUND_DIR)

    if not icon_paths or not background_paths:
        print("Error: Check if 'dataset_base' and 'diagram_base' directories contain images.")
        return

    total_icons = len(icon_paths)
    print(f"Found {total_icons} icons and {len(background_paths)} backgrounds.")
    print("-" * 50)

    # Prepare all tasks for parallel processing
    all_tasks = []
    for main_icon_path in tqdm(icon_paths, desc="Preparing tasks"):
        output_subdir = OUTPUT_DIR / main_icon_path.parent.name / main_icon_path.stem
        other_icon_paths = [p for p in icon_paths if p != main_icon_path]

        for j in range(NUM_VARIATIONS_PER_ICON):
            bg_path = random.choice(background_paths)
            task_data = {
                "main_icon_path": str(main_icon_path),
                "variation_index": j,
                "bg_path": str(bg_path),
                "other_icon_paths": [str(p) for p in other_icon_paths],
                "output_subdir": str(output_subdir),
            }
            all_tasks.append(task_data)

    total_operations = len(all_tasks)
    print(f"Prepared {total_operations} tasks for parallel processing")

    # Process tasks in parallel with progress bar
    successful_generations = []
    failed_generations = []

    with mp.Pool(processes=NUM_WORKERS) as pool:
        with tqdm(total=total_operations, desc="Generating dataset", unit="images") as pbar:
            for result in pool.imap_unordered(generate_single_variation, all_tasks):
                if result["success"]:
                    successful_generations.append(result)
                    pbar.set_postfix(
                        {
                            "Success": len(successful_generations),
                            "Failed": len(failed_generations),
                            "Current": f"{result['main_icon']}_{result['variation']:04d}",
                        }
                    )
                else:
                    failed_generations.append(result)
                    pbar.set_postfix(
                        {"Success": len(successful_generations), "Failed": len(failed_generations), "Last Error": result.get("reason", "Unknown")}
                    )

                pbar.update(1)

    print("\n--- Dataset generation process completed! ---")
    print(f"Successfully generated: {len(successful_generations)} images")
    print(f"Failed generations: {len(failed_generations)}")

    if failed_generations:
        print("\nSome generations failed. First few errors:")
        for failure in failed_generations[:3]:
            if "error" in failure:
                print(f"  - {failure['main_icon']}: {failure['error']}")
            else:
                print(f"  - {failure['main_icon']}: {failure.get('reason', 'Unknown error')}")


if __name__ == "__main__":
    main()
