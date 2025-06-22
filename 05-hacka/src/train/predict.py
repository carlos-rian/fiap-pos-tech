import json
import random
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import cv2
import torch
import torchvision
from PIL import Image

from src.train.util import PascalVOCDataset, get_model


def make_prediction(
    model: torch.nn.Module, image_path: Path, device: torch.device, confidence_threshold: float = 0.7
) -> tuple[list, list, list, int, int]:
    """
    Make a prediction on a single image.
    Returns boxes, labels, scores, and the original image dimensions.
    """
    image = Image.open(image_path).convert("RGB")
    image_width, image_height = image.size
    transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])
    image_tensor = transform(image).to(device)
    model.eval()
    with torch.no_grad():
        prediction = model([image_tensor])
    pred_scores = prediction[0]["scores"].detach().cpu().numpy()
    pred_boxes = prediction[0]["boxes"].detach().cpu().numpy()[pred_scores >= confidence_threshold]
    pred_labels = prediction[0]["labels"].detach().cpu().numpy()[pred_scores >= confidence_threshold]
    pred_scores = pred_scores[pred_scores >= confidence_threshold]
    return pred_boxes, pred_labels, pred_scores, image_width, image_height


@lru_cache(maxsize=None)
def create_color(text: str) -> tuple:
    """
    Generate a random color for a given text label.
    """
    random_color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )
    match random_color:
        case (r, g, b) if r + g + b > 650:
            t = f"{text}{random.randint(0, 10)}"
            color, _ = create_color(t)
        case _:
            color = random_color
    font_color = (255, 255, 255) if sum(color) < 500 else (0, 0, 0)
    return (color, font_color)


def draw_boxes_on_image(image_path: Path, boxes: list, labels: list, scores: list, class_map: dict, output_path: Path) -> None:
    """
    Draw bounding boxes and labels on the image and save the result.
    """
    image = cv2.imread(str(image_path))
    colors = {}
    for label_int in class_map.keys():
        colors[label_int] = create_color(str(label_int))
    for i, box in enumerate(boxes):
        xmin, ymin, xmax, ymax = map(int, box)
        label_int = labels[i]
        class_name = class_map.get(label_int, "Desconhecido")
        score = scores[i]
        color, font_color = colors.get(label_int, ((255, 255, 255), (0, 0, 0)))
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
        text = f"{class_name}: {score:.2f}"
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(image, (xmin, ymin - text_height - 10), (xmin + text_width, ymin), color, -1)
        cv2.putText(image, text, (xmin, ymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, font_color, 2)
    cv2.imwrite(str(output_path), image)
    print(f"✅ Imagem com as previsões salva em: {output_path}")


def format_predictions_as_json(
    boxes: list, labels: list, scores: list, class_map: dict[int, str], image_width: int, image_height: int, model_path: Path
) -> dict[str, Any]:
    """
    Format PyTorch predictions as a dictionary similar to AutoML output.
    """
    predictions_list = []
    for i, box in enumerate(boxes):
        xmin, ymin, xmax, ymax = box
        normalized_box = {
            "xMin": float(xmin / image_width),
            "yMin": float(ymin / image_height),
            "xMax": float(xmax / image_width),
            "yMax": float(ymax / image_height),
        }
        prediction_item = {"confidence": float(scores[i]), "displayName": class_map.get(labels[i], "Desconhecido"), "boundingBox": normalized_box}
        predictions_list.append(prediction_item)
    final_output = {"predictions": predictions_list, "modelInfo": {"type": "local_pytorch", "model_path": str(model_path)}}
    return final_output


def prepare_output_dirs(base_path: Path) -> tuple[Path, Path, Path]:
    """
    Cria diretórios de saída e retorna os caminhos para a base, imagem e JSON.
    """
    datetime_now = datetime.now().strftime("%Y%m%d%H%M")
    base_output = Path(f"{base_path}/predictions/{datetime_now}")
    output_image_path = base_output / "prediction.png"
    output_json_path = base_output / "prediction.json"
    base_output.mkdir(parents=True, exist_ok=True)
    return base_output, output_image_path, output_json_path


def load_class_map(dataset_path: Path) -> tuple[dict[int, str], int]:
    """
    Carrega o mapeamento de classes a partir do dataset PascalVOC.
    """
    temp_dataset = PascalVOCDataset(root_dir=dataset_path)
    num_classes = len(temp_dataset.class_to_int) + 1
    class_map = temp_dataset.int_to_class
    return class_map, num_classes


def load_trained_model(model_path: Path, num_classes: int, device: torch.device) -> torch.nn.Module:
    """
    Carrega o modelo treinado no dispositivo especificado.
    """
    model = get_model(num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    return model


def save_json_output(json_output: dict, output_json_path: Path) -> None:
    """
    Salva o resultado da predição em formato JSON.
    """
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=4)
    print(f"✅ Saída JSON salva em: {output_json_path}")


def show_image(image_path: Path) -> None:
    """
    Exibe a imagem anotada (útil em notebooks).
    """
    result_image = cv2.imread(str(image_path))
    try:
        cv2_imshow(result_image)
    except NameError:
        # cv2_imshow pode não estar disponível fora do Colab/Jupyter
        pass


def main(image_path: Path, model_path: Path, dataset_path: Path, base_path: Path) -> dict[str, Any]:
    """
    Executa a predição em uma imagem, salva a imagem anotada e o JSON, e exibe o resultado.
    """
    # Preparação dos diretórios de saída
    base_output, output_image_path, output_json_path = prepare_output_dirs(base_path)
    print(f"{model_path=}")
    print(f"{base_output=}")
    print(f"{output_image_path=}")
    print(f"{output_json_path=}")

    # Verificação da existência da imagem
    if not image_path.exists():
        print(f"❌ Erro: A imagem de teste '{image_path}' não foi encontrada.")
        print("Por favor, atualize o caminho da imagem.")
        return

    # Configuração de parâmetros
    confidence = 0.7
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Carregamento do mapeamento de classes
    print("Carregando mapeamento de classes...")
    class_map, num_classes = load_class_map(dataset_path)

    # Carregamento do modelo treinado
    print(f"Carregando modelo de '{model_path}'...")
    model = load_trained_model(model_path, num_classes, device)

    # Predição
    print(f"Fazendo previsão na imagem '{image_path}'...")
    boxes, labels, scores, img_width, img_height = make_prediction(model, image_path, device, confidence)
    print(f"Encontradas {len(boxes)} anotações. Desenhando na imagem...")

    # Desenho das caixas e salvamento dos resultados
    draw_boxes_on_image(image_path, boxes, labels, scores, class_map, output_image_path)
    json_output = format_predictions_as_json(boxes, labels, scores, class_map, img_width, img_height, model_path)
    save_json_output(json_output, output_json_path)
    show_image(output_image_path)
    return json_output
