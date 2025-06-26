import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import datetime

from src.finetunning.predict import run_prediction
from src.finetunning.util import get_class_from_prediction
from src.generative_ai.chatgpt import generate_stride_analysis

# add the src directory to the Python path

BASE_PATH = Path(__file__).resolve().parent

IMAGES_PATH_FOR_TEST = (BASE_PATH / "dataset/software-arch-image-for-test/").glob("*.png")
MODEL_PATH = BASE_PATH / "models/soft-arch_epoch-7_202506251807.pth"
DATASET_PATH = BASE_PATH / "dataset/dataset_augmented"
BASE_OUTPUT_PATH = BASE_PATH / "output"


for image_path in IMAGES_PATH_FOR_TEST:
    if not image_path.exists():
        raise FileNotFoundError(f"Image file {image_path} does not exist.")

    folder = datetime.now().strftime("%Y%m%d%H%M")
    base_path = BASE_OUTPUT_PATH / f"{image_path.stem}_{folder}"
    base_path.mkdir(parents=True, exist_ok=True)
    prediction = run_prediction(
        image_path=image_path, model_path=MODEL_PATH, dataset_path=DATASET_PATH, base_path=base_path, save_json=True, save_image=True
    )

    classes = get_class_from_prediction(prediction=prediction)

    stride_analysis = generate_stride_analysis(components=set(classes))

    for analysis in stride_analysis:
        print(f"\n--- Analysis for Component: {analysis.component_name} ---")
        print("-" * 45)
        for threat in analysis.threats:
            print(f"  Category:         {threat.threat_category.value}")
            print(f"  Threat:           {threat.threat_description}")
            print(f"  Countermeasure:   {threat.suggested_countermeasure}")
            print("-" * 45)

    # save the analysis to a file
    output_file = base_path / "stride_analysis.json"
    all_results = [analysis.model_dump(mode="json") for analysis in stride_analysis]
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)

    print(f"Stride analysis saved to {output_file}")
