from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CHECKPOINT_PATH = PROJECT_ROOT / "worker/models/I3D/_checkpoints/best_acc_top1_epoch_24.pth"
MODEL_CONFIG_PATH = PROJECT_ROOT / "worker/models/I3D/_settings/config.py"
DEVICE = "cpu"
LABELS = ["violence", "non-violence"]