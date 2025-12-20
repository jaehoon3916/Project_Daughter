import os
from dotenv import load_dotenv
import torch 

def set_device_cuda():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return device 

def get_model_api(model_type: str):
    load_dotenv()
    if model_type == "openai":
        api_key = os.getenv("OPENAI_KEY")
    elif model_type == "google":
        api_key = os.getenv("GEMINI_API_KEY")
    return api_key