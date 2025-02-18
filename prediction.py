import warnings
from ultralytics import YOLO
import numpy as np
import pandas as pd
from roboflow import Roboflow

rf = Roboflow(api_key="l295t4E7rkshIgYec4Vk")
project = rf.workspace().project("waste_segrication")

model = project.version(1).model

# Load a model
model_ = YOLO('models/last.pt')

class_labels = ["E-waste", "Recycle", "Trash"]


def predict(img_path):
    # results = model.predict(img_path)
    prediction = model.predict(img_path)
    prediction = prediction.json()
    probabilities = pd.DataFrame(
        prediction['predictions'][0]['predictions']).reset_index(drop=True).iloc[0].tolist()
    class_label = np.argmax(probabilities)
    class_target = class_labels[class_label]
    probability = (f"{round(probabilities[class_label],4)*100}%")

    return class_target, probability
