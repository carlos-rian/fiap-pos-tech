# FIAP POS Tech - Hackathon Project

## Overview
This project is a solution developed for the FIAP POS Tech Hackathon, focused on processing, augmentation, and analysis of image datasets, as well as integration with generative AI models and training of custom models.

## Make sure to download them before running the project
- [Software Architecture Dataset](https://www.kaggle.com/datasets/carlosrian/software-architecture-dataset): Download the dataset `dataset_augmented` folder from Kaggle and save it in the `src/dataset/` folder. The dataset is large (over 30GB) and contains images and XML files for training.
- [Software Arch Faster C-RNN Cloud Object Detection](https://www.kaggle.com/models/carlosrian/software-architecture-faster-crnn-cloud-object-detection):  Download the trained model `soft-arch_epoch-7_202506251807.pth` file from Kaggle and save it in the `src/models/` folder. The model is a custom Faster R-CNN trained on the dataset, with a size of approximately 160MB.

Note: The model was trained using just a `small subset of the dataset`, **so it is not expected to work well with the full dataset**. The model was trained to demonstrate the process of training and prediction using custom models.

## Kaggle Project Links

This project is hosted on Kaggle and includes the following links for training, prediction, and dataset augmentation:

- [Training *Code*](https://www.kaggle.com/code/carlosrian/soft-arch-predict-model) 
- [Prediction *Code*](https://www.kaggle.com/code/carlosrian/soft-arch-train-model)
- [Augmented *Dataset*](https://www.kaggle.com/datasets/carlosrian/software-architecture-dataset)
- [Trained Model *Data Card*](https://www.kaggle.com/models/carlosrian/software-architecture-faster-crnn-cloud-object-detection)

All images and XMLs used to train were saved in the `src/dataset/dataset_augmented/` folder and listed in the `dataset_output_image.csv` file.

## Project Structure

```
├── pyproject.toml           # Python project configuration
├── README.md                # Project documentation
├── uv.lock                  # Dependency lockfile
├── dataset_output_image.csv # CSV listing all images and XMLs used for training
├── src/
│   ├── main.py              # Main execution script
│   ├── dataset/
│   │   ├── augment_dataset.py            # Data augmentation script
│   │   ├── generate_dataset_output.py    # Dataset output generation
│   │   ├── dataset_augmented/            # Augmented images and annotations (PNG, XML)
│   │   ├── dataset_base/                 # Base image dataset
│   │   ├── dataset_output/               # Output from dataset processing
│   │   ├── diagram_base/                 # Original diagrams
│   │   ├── diagram_base_optimized/       # Optimized diagrams
│   │   ├── scripts/                      # Auxiliary scripts
│   │   └── test/                         # Dataset-related tests
│   ├── finetunning/
│   │   ├── predict.py      # Prediction script using trained model
│   │   ├── train.py        # Model training script
│   │   └── util.py         # Utilities for training/prediction
│   ├── generative_ai/
│   │   └── chatgpt.py      # Integration with generative AI (ChatGPT)
│   ├── models/
│   │   └── *.pth           # Trained models (PyTorch), please download from the link provided in the warnings section
│   └── output/
│       └── [date]/         # Outputs organized by date of execution
```

## Description of Modules and Folders

- **pyproject.toml**: Manages dependencies and Python project settings.
- **uv.lock**: Lockfile for dependency management with uv.
- **dataset_output_image.csv**: CSV file listing all images and XMLs used for training.
- **src/main.py**: Main entry point for running project flows.
- **src/dataset/**: Scripts and data for handling, augmenting, and testing image datasets.
  - **augment_dataset.py**: Performs data augmentation on images.
  - **generate_dataset_output.py**: Generates processed dataset outputs.
  - **dataset_augmented/**: Contains augmented images and their annotation files (e.g., .png, .xml).
  - **dataset_base/**: Original image dataset.
  - **dataset_output/**: Output from dataset processing.
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
- **src/output/**: Processing outputs and results, organized by date.

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
The project follows a structured workflow:

- **Dataset**:
   - [Dataset generation and processing](src/dataset/generate_dataset_output.py): Generates the dataset with various transformations. This step will generate 10 new images for each original image with different backgrounds, rotations, and other transformations.
   - [Data augmentation and processing](src/dataset/augment_dataset.py): Augments the dataset, generating 10 new images for each original image based on the generated dataset from the previous step.
- **Model Training**:
   - [Model training](src/finetunning/train.py): After the dataset is generated, this script trains a custom model using the augmented dataset.
- **Model Prediction**:
   - [Model prediction](src/finetunning/predict.py): Uses the trained model to make predictions on new images.
- **Generative AI**:
   - [Generative AI integration](src/generative_ai/chatgpt.py): Integrates with ChatGPT for generating text based on image analysis, using the predictions made by the model.
- **Output Generation**:
   - Outputs are generated in the `src/output/` directory, organized by date of execution.

## Requirements
- Python 3.12+
- UV (for dependency management)
- PyTorch
- OpenCV
- Other dependencies listed in `pyproject.toml`

## Dataset and Model Access

Due to size constraints, the dataset and trained model are not included in this repository. Request access from the project team using the following links:
- [Dataset Kagle link (+30GB)](https://www.kaggle.com/datasets/carlosrian/software-architecture-dataset) save the dataset in the `src/dataset/` folder.
- [Model Kagle link (+150MB)](https://www.kaggle.com/models/carlosrian/software-architecture-faster-crnn-cloud-object-detection) save the model in the `src/models/` folder.

## License
[MIT](LICENSE)
