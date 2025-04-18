import os
import re
import json
import pandas as pd
import torch
import datetime
import jsonlines
from vllm import LLM, SamplingParams
from thefuzz import process
from sklearn.metrics import precision_score, recall_score, f1_score

# Set environment & paths
os.environ['HF_HOME'] = os.path.join(os.path.abspath(os.path.join(os.getcwd(), '..')), "models/huggingface_cache")
DOWNLOAD_DIR = os.path.join(os.path.abspath(os.path.join(os.getcwd(), '..')), "models")
LLAMA_MODEL_PATH = "/datasets/ai/llama3/hub/models--meta-llama--Meta-Llama-3.1-8B-Instruct/snapshots/5206a32e0bd3067aef1ce90f5528ade7d866253f"
ZEHPYR_MODEL_PATH = "HuggingFaceH4/zephyr-7b-beta"

def get_sampling_params(max_tokens=300, temperature=0, top_p=0.9, stops=None):
    if stops is None:
        stops = ["</s>", "\n}"]
    return SamplingParams(
        n=1,
        temperature=temperature,
        max_tokens=max_tokens,
        stop=stops,
        top_p=top_p
    )

def get_llm(model_path=LLAMA_MODEL_PATH, tokenizer_path=None, download_dir=DOWNLOAD_DIR):
    if tokenizer_path is None:
        tokenizer_path = model_path
        
    return LLM(
        model=model_path,
        tokenizer=tokenizer_path,
        download_dir=download_dir,
        tensor_parallel_size=1
    )

def initialize_llm(model_path, tokenizer_path=None):
    return get_llm(model_path=model_path, tokenizer_path=tokenizer_path)