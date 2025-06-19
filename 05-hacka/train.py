import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

DATASET_PATH: Path = Path("dataset_augment")


class CustomObjectDetectionDataset(Dataset):
    def __init__(self, image_dir: Path, annotations_dir: Path, transforms: Optional[Any] = None):
        self.image_dir: Path = Path(image_dir)
        self.annotations_dir: Path = Path(annotations_dir)
        self.transforms: Optional[Any] = transforms
        self.image_files: List[str] = [f.name for f in self.image_dir.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png")]
        # Mapear nome da imagem para o arquivo de anotação
        self.image_to_xml: Dict[str, Path] = {
            Path(img_name).stem: self.annotations_dir / (Path(img_name).stem + ".xml") for img_name in self.image_files
        }
        # Mapear classes string para IDs numéricos (se necessário)
        self.class_to_id: Dict[str, int] = {"classe_a": 0, "classe_b": 1}  # Exemplo

    def __len__(self) -> int:
        return len(self.image_files)

    def __getitem__(self, idx: int) -> Tuple[Image.Image, Dict[str, torch.Tensor]]:
        img_name: str = self.image_files[idx]
        img_path: Path = self.image_dir / img_name
        xml_path: Optional[Path] = self.image_to_xml.get(Path(img_name).stem)

        image: Image.Image = Image.open(img_path).convert("RGB")

        boxes: List[List[float]] = []
        labels: List[int] = []
        if xml_path and xml_path.exists():
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for obj in root.findall("object"):
                class_name: str = obj.find("name").text
                xmin: float = float(obj.find("bndbox/xmin").text)
                ymin: float = float(obj.find("bndbox/ymin").text)
                xmax: float = float(obj.find("bndbox/xmax").text)
                ymax: float = float(obj.find("bndbox/ymax").text)
                boxes.append([xmin, ymin, xmax, ymax])
                labels.append(self.class_to_id[class_name])

        boxes_tensor: torch.Tensor = torch.as_tensor(boxes, dtype=torch.float32)
        labels_tensor: torch.Tensor = torch.as_tensor(labels, dtype=torch.int64)

        target: Dict[str, torch.Tensor] = {}
        target["boxes"] = boxes_tensor
        target["labels"] = labels_tensor
        target["image_id"] = torch.tensor([idx])  # Adicionar image ID

        if self.transforms:
            image, target = self.transforms(image, target)  # Se você tiver transforms que trabalham com imagem E target

        return image, target


# 4. Exemplo de DataLoader e Loop de Treinamento (PyTorch-like)
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.transforms import functional as F

# Defina suas transformações (normalização etc.)
# Você pode precisar de uma função `collate_fn` para detecção de objetos para lidar com diferentes números de objetos por imagem
from utils.collate_fns import collate_fn  # Ou implemente uma simples

dataset = CustomObjectDetectionDataset(image_dir=Path("pasta_local_imagens"), annotations_dir=Path("pasta_local_xml"), transforms=None)
data_loader = DataLoader(dataset, batch_size=2, shuffle=True, num_workers=4, collate_fn=collate_fn)

model = fasterrcnn_resnet50_fpn(pretrained=True)
# num_classes = len(dataset.class_to_id) # +1 for background in some models
# in_features = model.roi_heads.box_predictor.cls_score.in_features
# model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

# optimizer = torch.optim.SGD(model.parameters(), lr=0.005, momentum=0.9, weight_decay=0.0005)
# num_epochs = 10

# if torch.cuda.is_available():
#     model.cuda()

# for epoch in range(num_epochs):
#    for images, targets in data_loader:
#        images = list(image.to(device) for image in images)
#        targets = [{k: v.to(device) for k, v in t.items()} for t in targets]
#        loss_dict = model(images, targets)
#        losses = sum(loss for loss in loss_dict.values())
#        optimizer.zero_grad()
#        losses.backward()
#        optimizer.step()
#        print(f"Epoch: {epoch}, Loss: {losses.item()}")

# Salvando o modelo
# torch.save(model.state_dict(), "modelo_treinado.pth")# torch.save(model.state_dict(), "modelo_treinado.pth")
