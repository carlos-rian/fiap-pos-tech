import random
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple

import albumentations as A
import cv2
import numpy as np

# --- CONFIGURAÇÃO ---
# 1. Coloque suas imagens e XMLs exportados do Label Studio nesta pasta
INPUT_DIR: Path = Path("dataset_base")

# 2. As imagens e XMLs aumentados serão salvos aqui
OUTPUT_DIR: Path = Path("dataset_output")

# 3. Quantas variantes você quer criar POR IMAGEM ORIGINAL?
# Se você tem 2 imagens e colocar 100 aqui, terá 200 imagens no final.
AUGMENTATIONS_PER_IMAGE: int = 100
# --- FIM DA CONFIGURAÇÃO ---


# Função para ler os arquivos .xml do Pascal VOC
def parse_voc_xml(xml_file: Path) -> Tuple[List[List[int]], List[str]]:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    bboxes: List[List[int]] = []
    labels: List[str] = []
    for member in root.findall("object"):
        label = member.find("name").text
        xmin = int(member.find("bndbox").find("xmin").text)
        ymin = int(member.find("bndbox").find("ymin").text)
        xmax = int(member.find("bndbox").find("xmax").text)
        ymax = int(member.find("bndbox").find("ymax").text)
        bboxes.append([xmin, ymin, xmax, ymax])
        labels.append(label)
    return bboxes, labels


# Função para criar um novo arquivo .xml do Pascal VOC
def create_voc_xml(
    image_path: Path, bboxes: List[List[int]], labels: List[str], output_dir: Path
) -> None:
    image_name: str = image_path.name
    height, width, _ = cv2.imread(str(image_path)).shape

    annotation = ET.Element("annotation")
    ET.SubElement(annotation, "folder").text = output_dir.name
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
    xml_filename: str = image_path.stem + ".xml"
    tree.write(output_dir / xml_filename)


# Define a pipeline de aumentação. Estas são transformações seguras para diagramas.
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


# Cria as pastas se não existirem
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

print(f"Coloque suas imagens e XMLs na pasta: '{INPUT_DIR}' e rode o script novamente.")

# Loop principal
image_files: List[Path] = [
    f for f in INPUT_DIR.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg")
]

for image_file in image_files:
    xml_file: Path = INPUT_DIR / (image_file.stem + ".xml")

    if not xml_file.exists():
        print(f"Aviso: Arquivo XML não encontrado para {image_file.name}. Pulando.")
        continue

    image: np.ndarray = cv2.imread(str(image_file))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    bboxes, class_labels = parse_voc_xml(xml_file)

    print(
        f"Processando {image_file.name} e gerando {AUGMENTATIONS_PER_IMAGE} variações..."
    )

    for i in range(AUGMENTATIONS_PER_IMAGE):
        transformed = transform(image=image, bboxes=bboxes, class_labels=class_labels)

        transformed_image: np.ndarray = transformed["image"]
        transformed_bboxes: List[List[int]] = transformed["bboxes"]
        transformed_labels: List[str] = transformed["class_labels"]

        # Gera um nome de arquivo único para a imagem aumentada
        output_filename_base: str = f"{image_file.stem}_aug_{i}"
        output_image_path: Path = OUTPUT_DIR / f"{output_filename_base}.png"

        # Salva a imagem aumentada
        cv2.imwrite(
            str(output_image_path), cv2.cvtColor(transformed_image, cv2.COLOR_RGB2BGR)
        )

        # Cria e salva o XML correspondente
        create_voc_xml(
            output_image_path, transformed_bboxes, transformed_labels, OUTPUT_DIR
        )

print("\nProcesso de aumentação concluído!")
print(f"Seu novo dataset está pronto na pasta: '{OUTPUT_DIR}'")
print(f"Seu novo dataset está pronto na pasta: '{OUTPUT_DIR}'")
