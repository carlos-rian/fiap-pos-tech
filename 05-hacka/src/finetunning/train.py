from datetime import datetime
from pathlib import Path

import torch
from tqdm.notebook import tqdm

from .util import PascalVOCDataset, get_model, get_transform

MODEL_NAME: str = None
MODEL_PATH: Path = None
BUCKER_PATH = Path("src/dataset")
DATASET_PATH: Path = BUCKER_PATH / "dataset_augment"


def train() -> None:
    """
    Train a Faster R-CNN model on the Pascal VOC-style dataset and save the trained model.
    """
    global MODEL_NAME, MODEL_PATH, DATASET_PATH
    datetime_now = datetime.now().strftime("%Y%m%d%H%M")
    NUM_EPOCHS = 10
    MODEL_PATH = DATASET_PATH.parent / "models" / f"soft-arch_epoch-{NUM_EPOCHS}_{datetime_now}.pth"
    MODEL_NAME = MODEL_PATH.name
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"{NUM_EPOCHS=}")
    print(f"{MODEL_PATH=}")
    print(f"{MODEL_NAME=}")
    print(f"{DEVICE=}")

    dataset = PascalVOCDataset(root_dir=DATASET_PATH, transforms=get_transform())
    num_classes = len(dataset.class_to_int) + 1
    indices = torch.randperm(len(dataset)).tolist()
    train_size = int(0.8 * len(dataset))
    dataset_train = torch.utils.data.Subset(dataset, indices[:train_size])

    def collate_fn(batch):
        return tuple(zip(*batch))

    data_loader_train = torch.utils.data.DataLoader(dataset_train, batch_size=2, shuffle=True, num_workers=2, collate_fn=collate_fn)
    # dataset_val = torch.utils.data.Subset(dataset, indices[train_size:])
    # data_loader_val = torch.utils.data.DataLoader(
    #     dataset_val, batch_size=1, shuffle=False, num_workers=2, collate_fn=collate_fn
    # )
    model = get_model(num_classes)
    model.to(DEVICE)
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)
    for epoch in tqdm(range(NUM_EPOCHS), desc="Epochs"):
        model.train()
        total_loss = 0
        for images, targets in tqdm(data_loader_train, desc="Batches"):
            images = list(image.to(DEVICE) for image in images)
            targets = [{k: v.to(DEVICE) for k, v in t.items()} for t in targets]
            loss_dict = model(images, targets)
            losses = sum(loss for loss in loss_dict.values())
            optimizer.zero_grad()
            losses.backward()
            optimizer.step()
            total_loss += losses.item()
        avg_loss = total_loss / len(data_loader_train)
        print(f"Epoch {epoch + 1}/{NUM_EPOCHS}, Loss de Treino: {avg_loss:.4f}", sep="\n")
        lr_scheduler.step()

    torch.save(model.state_dict(), MODEL_PATH)
    print(f"Treinamento concluído! Modelo salvo como '{MODEL_PATH}'")


if __name__ == "__main__":
    train()
    print(f"Modelo treinado: {MODEL_NAME}")
    print(f"Modelo salvo em: {MODEL_PATH}")
    print(f"Dataset usado: {DATASET_PATH}")
