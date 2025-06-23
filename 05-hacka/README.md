# FIAP POS Tech - Hackathon Project

## Overview
This project is a solution developed for the FIAP POS Tech Hackathon, focused on processing, augmentation, and analysis of image datasets, as well as integration with generative AI models and training of custom models.

## Warnings (Files/Directories not available)
- **src/dataset/dataset_augment/**: The official dataset used in this project is not publicly available, because it is too large to upload to GitHub. Request access to the dataset from the [Google Drive link +100GB](https://drive.google.com/file/d/1D3fADFR0UmFvyX54-iIRkyGX4QPjZGPa/view?usp=drive_link) provided by the project team.
- **src/models/** The model trained in this project is not publicly available, because it is too large to upload to GitHub. Request access to the model from the [Google Drive link](https://drive.google.com/file/d/1gXZm0NloL2bhaJoEXVPDfNri98f00ZZQ/view?usp=drive_link) provided by the project team.


## Project Structure

```
├── pyproject.toml           # Python project configuration
├── README.md                # Project documentation
├── uv.lock                  # Dependency lockfile
├── src/
│   ├── main.py              # Main execution script
│   └── dataset/
│       ├── augment_dataset.py           # Data augmentation script
│       ├── generate_dataset_output.py   # Dataset output generation
│       ├── dataset_augment/            # Augmented images and annotations
│       ├── dataset_base/               # Base image dataset
│       ├── diagram_base/               # Original diagrams
│       ├── diagram_base_optimized/     # Optimized diagrams
│       ├── scripts/                    # Auxiliary scripts
│       └── test/                       # Dataset-related tests
│   ├── finetunning/
│       ├── predict.py      # Prediction script using trained model
│       ├── train.py        # Model training script
│       └── util.py         # Utilities for training/prediction
│   ├── generative_ai/
│       └── chatgpt.py      # Integration with generative AI (ChatGPT)
│   ├── models/
│       └── *.pth           # Trained models (PyTorch)
│   └── output/
│       ├── aws/            # Outputs related to images from dataset/test/aws
│       └── az/             # Outputs related to images from dataset/test/az
```

## Description of Modules and Folders

- **pyproject.toml**: Manages dependencies and Python project settings.
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
- PyTorch
- OpenCV
- Other dependencies listed in `pyproject.toml`

## License
[MIT](LICENSE)
