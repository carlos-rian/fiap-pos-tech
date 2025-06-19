import csv
import random
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

import cv2

# --- ESTRUTURAS DE DADOS ---
# Usamos dataclasses para criar objetos de dados claros e tipados.


@dataclass
class BoundingBox:
    """Representa uma única caixa de anotação normalizada."""

    label: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float


@dataclass
class ImageAnnotation:
    """Agrupa todas as anotações de uma única imagem."""

    image_filename: str
    gcs_path: str
    boxes: List[BoundingBox] = field(default_factory=list)
    ml_use: Optional[str] = None


# --- CLASSE PRINCIPAL ---


class AutoMLDatasetGenerator:
    """
    Gera um arquivo CSV para importação no Google AutoML Vision Object Detection.

    O processo segue as melhores práticas:
    1. Lê e normaliza todos os dados de origem (XMLs).
    2. Agrupa as anotações por imagem.
    3. Embaralha a lista de imagens.
    4. Atribui os conjuntos (TRAIN, VALIDATION, TEST) às imagens embaralhadas.
    5. Escreve o arquivo CSV final.
    """

    def __init__(
        self,
        input_dir: Path,
        gcs_bucket_name: str,
        output_csv_path: Path,
        train_split: float = 0.8,
        validation_split: float = 0.1,
    ):
        """
        Inicializa o gerador de dataset.

        Args:
            input_dir: Caminho para a pasta contendo os arquivos .png e .xml.
            gcs_bucket_name: Nome do bucket no Google Cloud Storage.
            output_csv_path: Caminho completo para o arquivo CSV de saída.
            train_split: Proporção de dados para o conjunto de treino (ex: 0.8 para 80%).
            validation_split: Proporção de dados para o conjunto de validação (ex: 0.1 para 10%).
                              O restante será usado para o conjunto de teste.
        """
        self.input_dir = input_dir
        self.gcs_bucket_name = gcs_bucket_name
        self.output_csv_path = output_csv_path
        self.train_split = train_split
        self.validation_split = validation_split
        self.image_annotations: List[ImageAnnotation] = []

    def _parse_and_normalize_xml(self, xml_path: Path) -> Tuple[str, List[BoundingBox]]:
        """Lê um arquivo XML e retorna dados de anotação normalizados."""
        tree = ET.parse(xml_path)
        root = tree.getroot()

        image_filename = root.findtext("filename", default=xml_path.with_suffix(".png").name)
        image_path = self.input_dir / image_filename

        try:
            size_node = root.find("size")
            img_width = int(size_node.findtext("width"))
            img_height = int(size_node.findtext("height"))
        except (AttributeError, TypeError):
            # Fallback: lê o tamanho diretamente da imagem se não estiver no XML
            img = cv2.imread(str(image_path))
            img_height, img_width, _ = img.shape

        boxes: List[BoundingBox] = []
        for member in root.findall("object"):
            label = member.findtext("name")
            bndbox = member.find("bndbox")
            xmin = float(bndbox.findtext("xmin"))
            ymin = float(bndbox.findtext("ymin"))
            xmax = float(bndbox.findtext("xmax"))
            ymax = float(bndbox.findtext("ymax"))

            boxes.append(
                BoundingBox(
                    label=label,
                    x_min=xmin / img_width,
                    y_min=ymin / img_height,
                    x_max=xmax / img_width,
                    y_max=ymax / img_height,
                )
            )
        return image_filename, boxes

    def process_source_data(self) -> None:
        """Encontra todos os XMLs, os processa e popula a lista de anotações."""
        print(f"🔎 Processando arquivos de anotação em '{self.input_dir}'...")
        xml_files = list(self.input_dir.glob("*.xml"))
        if not xml_files:
            print(f"⚠️ Nenhum arquivo .xml encontrado em '{self.input_dir}'.")
            return

        for xml_path in xml_files:
            filename, boxes = self._parse_and_normalize_xml(xml_path)
            self.image_annotations.append(
                ImageAnnotation(
                    image_filename=filename,
                    gcs_path=f"gs://{self.gcs_bucket_name}/{filename}",
                    boxes=boxes,
                )
            )
        print(f"✅ {len(self.image_annotations)} imagens processadas com sucesso.")

    def shuffle_and_split_data(self) -> None:
        """Embaralha as anotações de imagem e atribui os conjuntos de dados."""
        print("🔀 Embaralhando e dividindo o dataset...")
        random.shuffle(self.image_annotations)

        total_images = len(self.image_annotations)
        train_end_idx = int(total_images * self.train_split)
        validation_end_idx = train_end_idx + int(total_images * self.validation_split)

        for i, annotation in enumerate(self.image_annotations):
            if i < train_end_idx:
                annotation.ml_use = "TRAIN"
            elif i < validation_end_idx:
                annotation.ml_use = "VALIDATION"
            else:
                annotation.ml_use = "TEST"

        train_count = sum(1 for a in self.image_annotations if a.ml_use == "TRAIN")
        val_count = sum(1 for a in self.image_annotations if a.ml_use == "VALIDATION")
        test_count = sum(1 for a in self.image_annotations if a.ml_use == "TEST")
        print(f"📊 Divisão: {train_count} Treino, {val_count} Validação, {test_count} Teste.")

    def write_csv(self) -> None:
        """Escreve os dados processados no arquivo CSV de saída."""
        print(f"✍️ Escrevendo arquivo de saída em '{self.output_csv_path}'...")
        with open(self.output_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for annotation in self.image_annotations:
                if not annotation.boxes:
                    # Lida com imagens sem anotações, se houver
                    row = [annotation.ml_use, annotation.gcs_path, "", "", "", "", "", "", "", ""]
                    writer.writerow(row)
                else:
                    for box in annotation.boxes:
                        # Formato AutoML: SET,gcs_path,label,x_min,y_min,,,x_max,y_max,,
                        row = [
                            annotation.ml_use,
                            annotation.gcs_path,
                            box.label,
                            box.x_min,
                            box.y_min,
                            "",
                            "",  # Coordenadas de polígono vazias
                            box.x_max,
                            box.y_max,
                            "",
                            "",  # Coordenadas de polígono vazias
                        ]
                        writer.writerow(row)
        print("🎉 Arquivo CSV gerado com sucesso!")

    def run(self) -> None:
        """Executa o pipeline completo de geração de dataset."""
        self.process_source_data()
        if self.image_annotations:
            self.shuffle_and_split_data()
            self.write_csv()


# --- BLOCO DE EXECUÇÃO ---

if __name__ == "__main__":
    # Altere estes valores conforme necessário
    INPUT_FOLDER = Path("dataset_augment")
    GCS_BUCKET = "fiap-hacka/dataset_augment"
    OUTPUT_CSV = Path("labels2.csv")
    # --- FIM DAS CONFIGURAÇÕES ---

    # Garante que a pasta de entrada existe
    if not INPUT_FOLDER.is_dir():
        print(f"❌ Erro: A pasta de entrada '{INPUT_FOLDER}' não foi encontrada.")
        print("Certifique-se de que a pasta com os dados aumentados existe.")
    else:
        generator = AutoMLDatasetGenerator(
            input_dir=INPUT_FOLDER,
            gcs_bucket_name=GCS_BUCKET,
            output_csv_path=OUTPUT_CSV,
        )
        generator.run()
