from pathlib import Path

FILE_FOLDER = Path(__file__).parent / "files"
TRAIN_FILE = FILE_FOLDER / "trn.json"
TEST_FILE = FILE_FOLDER / "tst.json"
CLEAN_FILE = FILE_FOLDER / "clean_dataset.json"
FINE_TUNING_FILE = FILE_FOLDER / "fine_tuning.jsonl"
