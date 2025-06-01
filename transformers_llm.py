from langchain.llms.base import LLM
from pydantic import PrivateAttr
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
import time
API_URL = os.getenv("OLLAMA_API_URL")

class TransformersLLM(LLM):
    model_name: str = "Qwen/Qwen2.5-Coder-3B-Instruct"
    device: str = "cuda"
    max_new_tokens: int = 200

    _tokenizer: AutoTokenizer = PrivateAttr()
    _model: AutoModelForCausalLM = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        token = os.environ.get("HUGGINGFACE_TOKEN")
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            use_auth_token=token,
            use_fast=True
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map={"": "cuda"},
            use_auth_token=token
        )

    @property
    def _llm_type(self) -> str:
        return "transformers"

    def _call(self, prompt: str, stop=None) -> str:
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self.device)
        start = time.time()
        outputs = self._model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=False  # Greedy decoding for speed
        )
        elapsed = time.time() - start
        num_tokens = outputs.shape[1]
        print(f"Generated {num_tokens} tokens in {elapsed:.2f} seconds ({num_tokens/elapsed:.2f} tokens/sec)")
        response = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
