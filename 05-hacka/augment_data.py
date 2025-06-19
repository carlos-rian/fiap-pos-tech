import os
import xml.etree.ElementTree as ET

import albumentations as A
import cv2

# --- CONFIGURAÇÃO ---
# 1. Coloque suas imagens e XMLs exportados do Label Studio nesta pasta
INPUT_DIR = "dataset_base"

# 2. As imagens e XMLs aumentados serão salvos aqui
OUTPUT_DIR = "dataset_output"

# 3. Quantas variantes você quer criar POR IMAGEM ORIGINAL?
# Se você tem 2 imagens e colocar 100 aqui, terá 200 imagens no final.
AUGMENTATIONS_PER_IMAGE = 100
# --- FIM DA CONFIGURAÇÃO ---


# Função para ler os arquivos .xml do Pascal VOC
def parse_voc_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    bboxes = []
    labels = []
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
def create_voc_xml(image_path, bboxes, labels, output_dir):
    image_name = os.path.basename(image_path)
    height, width, _ = cv2.imread(image_path).shape

    annotation = ET.Element("annotation")
    ET.SubElement(annotation, "folder").text = os.path.basename(output_dir)
    ET.SubElement(annotation, "filename").text = image_name
    ET.SubElement(annotation, "path").text = image_path

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
    xml_filename = os.path.splitext(image_name)[0] + ".xml"
    tree.write(os.path.join(output_dir, xml_filename))


# Define a pipeline de aumentação. Estas são transformações seguras para diagramas.
transform = A.Compose(
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
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Coloque suas imagens e XMLs na pasta: '{INPUT_DIR}' e rode o script novamente.")

# Loop principal
image_files = [f for f in os.listdir(INPUT_DIR) if f.endswith((".png", ".jpg", ".jpeg"))]

for image_file in image_files:
    image_path = os.path.join(INPUT_DIR, image_file)
    xml_path = os.path.join(INPUT_DIR, os.path.splitext(image_file)[0] + ".xml")

    if not os.path.exists(xml_path):
        print(f"Aviso: Arquivo XML não encontrado para {image_file}. Pulando.")
        continue

    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    bboxes, class_labels = parse_voc_xml(xml_path)

    print(f"Processando {image_file} e gerando {AUGMENTATIONS_PER_IMAGE} variações...")

    for i in range(AUGMENTATIONS_PER_IMAGE):
        transformed = transform(image=image, bboxes=bboxes, class_labels=class_labels)

        transformed_image = transformed["image"]
        transformed_bboxes = transformed["bboxes"]
        transformed_labels = transformed["class_labels"]

        # Gera um nome de arquivo único para a imagem aumentada
        output_filename_base = f"{os.path.splitext(image_file)[0]}_aug_{i}"
        output_image_path = os.path.join(OUTPUT_DIR, f"{output_filename_base}.png")

        # Salva a imagem aumentada
        cv2.imwrite(output_image_path, cv2.cvtColor(transformed_image, cv2.COLOR_RGB2BGR))

        # Cria e salva o XML correspondente
        create_voc_xml(output_image_path, transformed_bboxes, transformed_labels, OUTPUT_DIR)

print("\nProcesso de aumentação concluído!")
print(f"Seu novo dataset está pronto na pasta: '{OUTPUT_DIR}'")
