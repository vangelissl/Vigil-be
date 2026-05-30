from mmaction2.mmaction.apis import init_recognizer
import os 

recognizer = init_recognizer(
    config="ml-service/models/I3D/_settings/config_heavy.py",
    checkpoint="ml-service/worker/models/I3D/_checkpoints/epoch_7.pth",
    device=os.environ["DEVICE"]
)