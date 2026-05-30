# ml-service/worker/inference.py
from .mmaction_compat import init_recognizer, inference_recognizer # type: ignore
import torch.nn.functional as F
from .result import ClassificationResult


class Recognizer:
    def __init__(self, config_path: str, checkpoint_path: str, device: str = "cuda"):
        self.model = init_recognizer(config_path, checkpoint_path, device)
        self.device = device
    
    def run_inference(self, video_path: str, labels: list[str], temperature: float = 2.0) -> ClassificationResult:
        result = inference_recognizer(self.model, video_path)
        result_dict = dict(result.all_items())

        predicted_label_id = result_dict["pred_label"].item()
        pred_scores_raw = result_dict["pred_score"].cpu()

        pred_scores = F.softmax(pred_scores_raw / temperature, dim=0).numpy().tolist()

        classification_result = ClassificationResult(
            predicted_class = labels[predicted_label_id],
            confidence = float(pred_scores[predicted_label_id]),
            all_scores={pair[0]: pair[1] for pair in zip(labels, pred_scores)}
        )

        return classification_result