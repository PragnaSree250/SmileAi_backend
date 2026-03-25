
import os
import numpy as np
from PIL import Image
import tensorflow as tf

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

def load_tflite_model(model_path):
    abs_path = os.path.join(MODELS_DIR, model_path)
    if not os.path.exists(abs_path):
        print(f"❌ Model not found: {abs_path}")
        return None
    try:
        interpreter = tf.lite.Interpreter(model_path=abs_path)
        interpreter.allocate_tensors()
        print(f"✅ Model loaded successfully: {model_path}")
        return interpreter
    except Exception as e:
        print(f"❌ Failed to load {model_path}: {e}")
        return None

if __name__ == "__main__":
    print(f"Checking models in: {MODELS_DIR}")
    load_tflite_model("clinical_diagnostic_model.tflite")
    load_tflite_model("smile_aesthetic_model.tflite")
    load_tflite_model("tooth_detection.tflite")
