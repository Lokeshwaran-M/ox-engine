import os
from llama_cpp import Llama
from typing import List, Dict, Union

from ox_engine.ai.prompt import Prompt


class Model:
    def __init__(self):

        self.md_path_base = os.path.join(os.path.expanduser("~"), "model.ox")
        os.makedirs(self.md_path_base, exist_ok=True)

    def load(self, md_path: str, **kwargs):
        md_path_parts = md_path.split("/")
        self.md_name = md_path_parts[2]
        self.md_path = os.path.join(self.md_path_base, md_path)
        self.model = Llama(
            model_path=self.md_path,
            n_gpu_layers=kwargs.get("n_gpu_layers", -1),
            seed=kwargs.get("seed", 1337),
            n_ctx=kwargs.get("n_ctx", 4096),
            n_threads=kwargs.get("n_threads", 8),
        )

    def generate(self, prompt: str, max_tokens: int = 50, **kwargs):

        res = self.model(prompt, max_tokens=max_tokens, echo=True, **kwargs)
        return res.get("choices")[0].get("text")

    def stream(self, prompt: str, **kwargs):
        output = self.model(prompt, stream=True, echo=False, **kwargs)
        for op in output:
            yield op.get("choices")[0].get("text") or ""
