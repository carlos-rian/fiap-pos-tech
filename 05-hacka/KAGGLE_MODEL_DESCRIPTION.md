# Software Architecture Cloud Object Detection Model - Faster R-CNN

## Model Overview

This is a **Faster R-CNN model** fine-tuned for detecting and classifying **cloud service components** in software architecture diagrams. The model was developed as part of a FIAP POS Tech Hackathon project and is specifically trained to identify AWS, Azure, and GCP service icons and components in technical diagrams.

## Model Architecture

- **Base Architecture**: Faster R-CNN with ResNet-50 backbone and Feature Pyramid Network (FPN)
- **Framework**: PyTorch
- **Pre-trained Weights**: COCO dataset (transfer learning)
- **Detection Head**: Custom FastRCNNPredictor for cloud service classification
- **Input Format**: RGB images (any resolution)
- **Output Format**: Bounding boxes with confidence scores and class labels

## Training Details

### Dataset
- **Training Images**: 400+ augmented software architecture diagrams
- **Annotation Format**: Pascal VOC XML
- **Classes**: 87+ unique cloud service components (AWS, Azure, GCP)
- **Data Split**: 80% training, 20% validation
- **Augmentation**: Multiple transformations applied while preserving bounding boxes

### Training Configuration
- **Epochs**: 10
- **Batch Size**: 2
- **Optimizer**: SGD (lr=0.005, momentum=0.9, weight_decay=0.0005)
- **Learning Rate Scheduler**: StepLR (step_size=3, gamma=0.1)
- **Device**: CUDA/CPU compatible
- **Loss Function**: Multi-task loss (classification + bounding box regression)

### Model Performance
- **Confidence Threshold**: 0.7 (default for inference)
- **Training Loss**: Progressively decreasing across epochs
- **Architecture Focus**: Optimized for technical diagram analysis
- **Real-time Inference**: Suitable for batch processing and real-time detection

## Supported Cloud Services

The model can detect and classify the following cloud service categories:

### AWS Services
- **Compute**: EC2, Lambda, Auto Scaling, ECS, EKS
- **Storage**: S3, EBS, EFS
- **Database**: RDS, DynamoDB, Aurora, Redshift
- **Networking**: VPC, Route 53, CloudFront, Load Balancing
- **Integration**: API Gateway, SQS, SNS
- **Management**: CloudWatch, CloudFormation

### Azure Services
- **Analytics**: Databricks
- **Storage**: Azure Storage, Managed Database
- **Compute**: Various Azure compute services
- **Networking**: Load Balancer, networking components
- **Management**: Azure management services

### GCP Services
- Various Google Cloud Platform components and services

## Technical Specifications

- **Model Size**: ~150MB
- **Input Resolution**: Variable (automatically handled)
- **Output Format**: JSON with bounding boxes and confidence scores
- **Inference Speed**: Optimized for batch processing
- **Memory Requirements**: GPU recommended (CUDA support)
- **Framework Dependencies**: PyTorch, torchvision, PIL, OpenCV

## Usage Examples

### Basic Inference
```python
# Load model
model = get_model(num_classes)
model.load_state_dict(torch.load('model.pth'))
model.eval()

# Make prediction
boxes, labels, scores, width, height = make_prediction(
    model, image_path, device, confidence_threshold=0.7
)
```

### Batch Processing
The model supports batch processing of multiple architecture diagrams for automated analysis.

## Output Format

The model outputs structured predictions:
```json
{
    "predictions": [
        {
            "confidence": 0.9979,
            "displayName": "aws_ec2_instance",
            "boundingBox": {
                "xMin": 0.321,
                "yMin": 0.354,
                "xMax": 0.401,
                "yMax": 0.460
            }
        }
    ]
}
```

## Applications

### Primary Use Cases
- **Automated Diagram Analysis**: Parse software architecture diagrams
- **Cloud Infrastructure Auditing**: Identify services in existing diagrams
- **Documentation Generation**: Extract service lists from visual diagrams
- **Architecture Compliance**: Validate diagram components against standards
- **Educational Tools**: Interactive learning for cloud architecture

### Integration Scenarios
- **CI/CD Pipelines**: Automated architecture validation
- **Documentation Tools**: Integration with technical writing platforms
- **Monitoring Systems**: Real-time architecture change detection
- **Design Tools**: Integration with diagramming software

## Model Limitations

- **Training Scope**: Trained on a subset of available cloud services
- **Diagram Types**: Optimized for standard architecture diagrams
- **Performance Note**: Best results on clear, well-structured diagrams
- **Language**: Primarily trained on English service names

## File Structure

```
models/
├── soft-arch_epoch-10_YYYYMMDDHHMM.pth    # Trained model weights
```

## Requirements

### Python Dependencies
```
torch>=1.9.0
torchvision>=0.10.0
Pillow>=8.0.0
opencv-python>=4.5.0
numpy>=1.21.0
```

### Hardware Requirements
- **GPU**: NVIDIA GPU with CUDA support (recommended)
- **RAM**: 8GB+ recommended
- **Storage**: 200MB for model files

## Citation

If you use this model in your research, please cite:
```
Software Architecture Cloud Object Detection Model
FIAP POS Tech Hackathon Project, 2025
Based on Faster R-CNN architecture with ResNet-50 backbone
```

## Related Resources

- **Dataset**: [Software Architecture Dataset](https://www.kaggle.com/datasets/carlosrian/software-architecture-dataset)
- **Documentation**: Complete training and inference scripts included
- **Code Repository**: Full implementation available

## Tags
`object-detection` `faster-rcnn` `pytorch` `cloud-computing` `aws` `azure` `gcp` `software-architecture` `computer-vision` `resnet50` `fpn` `technical-diagrams`
