# FIAP POS Tech - Hackathon Project

## Overview
This project is a solution developed for the FIAP POS Tech Hackathon, focused on processing, augmentation, and analysis of image datasets, as well as integration with generative AI models and training of custom models.

## Warnings (Files/Directories not available) - Make sure to download them before running the project
- **src/dataset/dataset_augmented/**: The official dataset used in this project is not publicly available, because it is too large to upload to GitHub. Download the dataset from the [Google Drive link +15GB](https://drive.google.com/file/d/1lTQnRcJTHsUiRcrEUHENfaY8Tietpknp/view?usp=sharing) provided by the project team.
- **src/models/** The model trained in this project is not publicly available, because it is too large to upload to GitHub. Download the model from the [Google Drive link +150MB](https://drive.google.com/file/d/1sHd2LTZTBwic3TRDgF_e6AI5Pz_btvUA/view?usp=sharing) provided by the project team.


Note: The model was trained using just a small subset of the dataset, so it is not expected to work well with the full dataset. The model was trained to demonstrate the process of training and prediction using custom models.

All images and XMLs used to train were saved in the `src/dataset/dataset_augment/` folder and listed in the `dataset_output_image.csv` file.

## Project Structure

```
├── pyproject.toml           # Python project configuration
├── README.md                # Project documentation
├── uv.lock                  # Dependency lockfile
├── src/
│   ├── main.py              # Main execution script
│   └── dataset/
│       ├── augment_dataset.py            # Data augmentation script
│       ├── generate_dataset_output.py    # Dataset output generation
│       ├── dataset_augmented/            # Augmented images and annotations, please download from the link provided in the warnings section
│       ├── dataset_base/                 # Base image dataset
│       ├── diagram_base/                 # Original diagrams
│       ├── diagram_base_optimized/       # Optimized diagrams
│       ├── scripts/                      # Auxiliary scripts
│       └── test/                         # Dataset-related tests
│   ├── finetunning/
│       ├── predict.py      # Prediction script using trained model
│       ├── train.py        # Model training script
│       └── util.py         # Utilities for training/prediction
│   ├── generative_ai/
│       └── chatgpt.py      # Integration with generative AI (ChatGPT)
│   ├── models/
│       └── *.pth           # Trained models (PyTorch), please download from the link provided in the warnings section
│   └── output/
│       ├── aws/            # Outputs related to images from dataset/test/aws
│       └── az/             # Outputs related to images from dataset/test/az
```

## Description of Modules and Folders

- **pyproject.toml**: Manages dependencies and Python project settings.
- **uv.lock**: Lockfile for dependency management with uv.
- **src/main.py**: Main entry point for running project flows.
- **src/dataset/**: Scripts and data for handling, augmenting, and testing image datasets.
  - **augment_dataset.py**: Performs data augmentation on images.
  - **generate_dataset_output.py**: Generates processed dataset outputs.
  - **dataset_augment/**: Contains augmented images and their annotation files (e.g., .png, .xml).
  - **dataset_base/**: Original image dataset.
  - **diagram_base/** and **diagram_base_optimized/**: Original and optimized diagrams.
  - **scripts/**: Auxiliary scripts for data handling.
  - **test/**: Test scripts for data validation.
- **src/finetunning/**: Scripts for training, prediction, and utilities for custom models.
  - **train.py**: Model training (e.g., PyTorch).
  - **predict.py**: Prediction using trained models.
  - **util.py**: Utility functions for the ML pipeline.
- **src/generative_ai/**: Integration with generative AI models.
  - **chatgpt.py**: Communication with the ChatGPT API.
- **src/models/**: Stores trained models (.pth).
- **src/output/**: Processing outputs and results, organized by provider (e.g., aws, az).

## How to Run

That step just works if you have the dataset and model files available, otherwise you will need to generate them using the scripts provided in the project.

1. Install dependencies:
   ```bash
   uv sync --python 3.12
   ```

2. Run the main script or specific scripts:
   ```bash
   python src/main.py
   ```

3. To train models:
   ```bash
   python src/finetunning/train.py
   ```

4. For prediction:
   ```bash
   python src/finetunning/predict.py
   ```


## Workflows
The project follows a structured workflows:

- **Dataset**:
   - [Dataset generation and processing](src/dataset/generate_dataset_output.py): Generates the dataset with various transformations the step will generate 10 new images for each original image with different background, rotation, and other transformations.
   - [Data augmentation and processing](src/dataset/augment_dataset.py): Augments the dataset will generate 10 new images for each original image based on the generated dataset run in the previous step.
- **Model Training**:
   - [Model training](src/finetunning/train.py): After the dataset is generated, this script trains a custom model using the augmented dataset.
- **Model Prediction**:
   - [Model prediction](src/finetunning/predict.py): Uses the trained model to make predictions on new images.
- **Generative AI**:
   - [Generative AI integration](src/generative_ai/chatgpt.py): Integrates with ChatGPT for generating text based on image analysis, the analysis is based on the predictions made by the model.
- **Output Generation**:
   - Outputs are generated in the `src/output/` directory, organized by image name for example image `aws.png` -> `src/output/aws/`.


## Requirements
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- PyTorch
- OpenCV
- Other dependencies listed in `pyproject.toml`

## Dataset and Model Access

Due to size constraints, the dataset and trained model are not included in this repository. Request access from the project team using the following links:
- [Dataset Google Drive link (+100GB)](https://drive.google.com/file/d/1D3fADFR0UmFvyX54-iIRkyGX4QPjZGPa/view?usp=drive_link)
- [Model Google Drive link](https://drive.google.com/file/d/1gXZm0NloL2bhaJoEXVPDfNri98f00ZZQ/view?usp=drive_link)

## License
[MIT](LICENSE)
