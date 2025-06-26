# Software Architecture Diagram Dataset - Augmented Cloud Services

## Dataset Overview

This dataset contains **augmented software architecture diagrams** specifically focused on **cloud service components** from major cloud providers (AWS, Azure, GCP). The dataset was developed as part of a FIAP POS Tech Hackathon project for training computer vision models to detect and classify cloud architecture components in technical diagrams.

## Dataset Contents

- **400+ augmented images** (PNG format) with corresponding Pascal VOC XML annotations
- **Cloud service components** from AWS, Azure, and GCP platforms
- **87 unique cloud service types** including:
  - AWS services: EC2, S3, RDS, DynamoDB, Lambda, API Gateway, CloudFront, etc.
  - Azure services: Databricks, Storage, Managed Database, Load Balancer, etc.
  - GCP services: (various Google Cloud Platform components)

## Data Augmentation Process

The dataset was created using a sophisticated augmentation pipeline that applies multiple transformations while preserving bounding box annotations:

### Augmentation Techniques Applied:
- **Brightness and contrast adjustments** (±20%)
- **Rotation** (±15 degrees)
- **Gaussian blur** (sigma: 0.0-2.0)
- **Gaussian noise** (variance: 10-50)
- **Elastic transformations** (alpha: 1, sigma: 50)
- **Grid distortions** (num_steps: 5, distort_limit: 0.3)
- **Optical distortions** (distort_limit: 0.1, shift_limit: 0.1)

### Quality Control:
- **Relevance filtering**: Only "High" relevance components were selected for augmentation
- **Bounding box preservation**: All transformations maintain accurate object detection annotations
- **Format compatibility**: Pascal VOC XML format for seamless integration with popular ML frameworks

## Technical Specifications

- **Image Format**: PNG
- **Annotation Format**: Pascal VOC XML
- **Augmentation Ratio**: 10 variations per original image
- **Image Categories**: Cloud architecture components and services
- **Bounding Box Accuracy**: Preserved through geometric transformations

## Use Cases

This dataset is ideal for:
- **Object detection** in software architecture diagrams
- **Cloud service recognition** in technical documentation
- **Automated diagram analysis** tools
- **Computer vision research** in technical domain
- **Training custom models** for architecture diagram parsing

## Dataset Structure

```
dataset_augmented/
├── image_xpto.png      # Augmented PNG images
├── image_xpto.xml      # Pascal VOC XML files
```

## Machine Learning Applications

Perfect for training:
- **YOLO** object detection models
- **Faster R-CNN** for precise component detection
- **Custom CNN architectures** for diagram analysis
- **Multi-class classification** models

## Quality Assurance

- All images maintain visual quality after augmentation
- Bounding boxes are accurately transformed with image modifications
- Consistent naming convention for easy batch processing
- Validated XML structure for error-free training

## Citation

If you use this dataset in your research, please cite:
```
Software Architecture Dataset - Augmented Cloud Services
FIAP POS Tech Hackathon Project, 2025
Based on Faster R-CNN architecture with ResNet-50 backbone
```

## Tags
`computer-vision` `object-detection` `cloud-computing` `software-architecture` `aws` `azure` `gcp` `augmented-data` `pascal-voc` `diagram-analysis`
