import os
import cv2
import configparser
import supervision as sv
from roboflow import Roboflow

# Get Roboflow API key from .env file
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_file = os.path.join(project_root, ".env")
config = configparser.ConfigParser()
config.read(env_file)
ROBOFLOW_API_KEY = config.get("settings", "ROBOFLOW_API_KEY")


def annotate_image(image_path):
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
    project = rf.workspace().project("gauss-3")
    model = project.version(1).model

    result = model.predict(image_path, confidence=40, overlap=30).json()

    labels = [item["class"] for item in result["predictions"]]

    detections = sv.Detections.from_inference(result)

    label_annotator = sv.LabelAnnotator()
    bounding_box_annotator = sv.BoundingBoxAnnotator()

    image = cv2.imread(image_path)

    annotated_image = bounding_box_annotator.annotate(
        scene=image, detections=detections
    )
    annotated_image = label_annotator.annotate(
        scene=annotated_image, detections=detections, labels=labels
    )

    # Enregistrer l'image annotée sur disque
    annotated_image_path = os.path.splitext(image_path)[0] + "_annotated.jpg"
    cv2.imwrite(annotated_image_path, annotated_image)

    return annotated_image_path
