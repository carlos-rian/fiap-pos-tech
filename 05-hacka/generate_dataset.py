import random
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Tuple
from xml.dom import minidom

from PIL import Image, ImageEnhance

# --- CONFIGURAÇÃO ---
BASE_DIR: Path = Path(__file__).parent
ICON_DIR: Path = BASE_DIR / "dataset_base/"
BACKGROUND_DIR: Path = BASE_DIR / "diagram_base/"
OUTPUT_DIR: Path = BASE_DIR / "dataset_output/"

# Parâmetros de geração
# NÚMERO DE VARIAÇÕES A SEREM CRIADAS PARA CADA ÍCONE.
NUM_VARIATIONS_PER_ICON: int = 100
MIN_TOTAL_ICONS_PER_IMAGE: int = 3
MAX_TOTAL_ICONS_PER_IMAGE: int = 10

# Parâmetros de aumentação (aumentation)
ICON_SIZE_RANGE: Tuple = (64, 96, 128, 192, 256)
ROTATION_RANGE: Tuple[float, float] = (-5.0, 5.0)
BRIGHTNESS_RANGE: Tuple[float, float] = (0.8, 1.2)
CONTRAST_RANGE: Tuple[float, float] = (0.8, 1.2)
# --- FIM DA CONFIGURAÇÃO ---

AnnotationObject = Dict[str, Any]


def get_asset_paths(directory: Path) -> List[Path]:
    """Busca recursivamente por todos os arquivos de imagem em um diretório."""
    return list(directory.glob("**/*.png")) + list(directory.glob("**/*.jpg"))


def augment_icon(icon_image: Image.Image) -> Image.Image:
    """Aplica uma série de transformações de aumentação a uma imagem de ícone."""
    new_size = random.choice(ICON_SIZE_RANGE)
    icon_image.thumbnail((new_size, new_size), Image.Resampling.LANCZOS)
    rotation_angle = random.uniform(*ROTATION_RANGE)
    icon_image = icon_image.rotate(rotation_angle, expand=True, resample=Image.Resampling.BICUBIC)
    enhancer = ImageEnhance.Brightness(icon_image)
    icon_image = enhancer.enhance(random.uniform(*BRIGHTNESS_RANGE))
    enhancer = ImageEnhance.Contrast(icon_image)
    icon_image = enhancer.enhance(random.uniform(*CONTRAST_RANGE))
    return icon_image


def generate_pascal_voc_xml(folder_name: str, image_filename: str, image_size: Tuple[int, int, int], objects: List[AnnotationObject]) -> str:
    """Gera uma string XML formatada no padrão Pascal VOC."""
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


def paste_icon_and_get_annotation(image: Image.Image, icon_path: Path) -> AnnotationObject:
    """Abre, aumenta, cola um ícone na imagem e retorna sua anotação."""
    with Image.open(icon_path).convert("RGBA") as icon_image:
        augmented_icon = augment_icon(icon_image.copy())
        max_x = image.width - augmented_icon.width
        max_y = image.height - augmented_icon.height

        # Retorna None se o ícone for maior que a imagem para evitar erro
        if max_x < 0 or max_y < 0:
            return None

        paste_x = random.randint(0, max_x)
        paste_y = random.randint(0, max_y)
        image.paste(augmented_icon, (paste_x, paste_y), augmented_icon)

        return {
            "label": icon_path.stem,
            "box": (paste_x, paste_y, paste_x + augmented_icon.width, paste_y + augmented_icon.height),
        }


def main() -> None:
    """Função principal para orquestrar a geração do dataset focada no ícone."""
    print("--- Iniciando Geração de Dataset (Lógica Focada no Ícone) ---")

    if OUTPUT_DIR.exists():
        print(f"Limpando diretório de saída existente: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    icon_paths = get_asset_paths(ICON_DIR)
    background_paths = get_asset_paths(BACKGROUND_DIR)

    if not icon_paths or not background_paths:
        print("Erro: Verifique se os diretórios 'dataset_base' e 'diagram_base' contêm imagens.")
        return

    total_icons = len(icon_paths)
    total_variations = total_icons * NUM_VARIATIONS_PER_ICON
    print(f"Encontrados {total_icons} ícones e {len(background_paths)} fundos.")
    print(f"Serão geradas {NUM_VARIATIONS_PER_ICON} variações por ícone, totalizando {total_variations} imagens.")
    print("-" * 50)

    # Loop principal: itera sobre cada ÍCONE
    for i, main_icon_path in enumerate(icon_paths):
        print(f"\n[Ícone {i + 1}/{total_icons}] Processando: {main_icon_path.name}", sep="\n")

        # Cria um diretório de saída específico para este ícone
        output_subdir = OUTPUT_DIR / main_icon_path.parent.name / main_icon_path.stem
        output_subdir.mkdir(parents=True, exist_ok=True)
        print(f"  Criado diretório: {output_subdir}", sep="\n")

        # Cria a lista de outros ícones (todos, exceto o principal)
        other_icon_paths = [p for p in icon_paths if p != main_icon_path]

        # Loop secundário: cria N variações para o ícone atual
        for j in range(NUM_VARIATIONS_PER_ICON):
            # Escolhe um fundo aleatório para esta variação
            bg_path = random.choice(background_paths)
            with Image.open(bg_path).convert("RGBA") as bg_image:
                annotations: List[AnnotationObject] = []

                # 1. Adiciona o ÍCONE PRINCIPAL
                main_annotation = paste_icon_and_get_annotation(bg_image, main_icon_path)
                if main_annotation:
                    annotations.append(main_annotation)

                # 2. Adiciona os ÍCONES DE CONTEXTO
                num_total_icons = random.randint(MIN_TOTAL_ICONS_PER_IMAGE, MAX_TOTAL_ICONS_PER_IMAGE)
                num_other_icons_to_add = num_total_icons - 1

                for _ in range(num_other_icons_to_add):
                    if not other_icon_paths:
                        continue
                    other_icon_path = random.choice(other_icon_paths)
                    other_annotation = paste_icon_and_get_annotation(bg_image, other_icon_path)
                    if other_annotation:
                        annotations.append(other_annotation)

                # 3. Salva a imagem e o XML
                if not annotations:
                    print(f"    Aviso: Nenhuma anotação foi criada para a variação {j}.")
                    continue

                base_filename = f"{main_icon_path.stem}_{j:04d}"
                image_filename = f"{base_filename}{bg_path.suffix}"
                xml_filename = f"{base_filename}.xml"

                final_image = bg_image.convert("RGB")
                final_image.save(output_subdir / image_filename, "PNG")

                xml_content = generate_pascal_voc_xml(output_subdir.name, image_filename, (bg_image.width, bg_image.height, 3), annotations)
                (output_subdir / xml_filename).write_text(xml_content, encoding="utf-8")

                if (j % 5 == 0) or (j == NUM_VARIATIONS_PER_ICON - 1):
                    print(f"    -> Gerada variação {j + 1}/{NUM_VARIATIONS_PER_ICON}", sep="\n")

    print("-" * 50)
    print("\n--- Processo de geração concluído! ---")
    print(f"Estrutura de diretórios por ícone criada em: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
