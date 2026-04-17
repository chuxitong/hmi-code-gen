"""
Wrapper around the real UI2Code^N visual language model.

The model ID is ``zai-org/UI2Code_N``. It is a 9B-parameter VLM built on
GLM-4.1V-9B-Base. On a consumer laptop GPU (RTX 3060 Laptop, 6 GB VRAM)
the model does not fit in bf16, so we load it with 4-bit quantisation and
let accelerate offload the rest to CPU/RAM automatically.

The class follows the same ``generate / refine / edit`` interface that the
rule-based stand-in exposes, so it can be dropped into the local HTTP
service and evaluation scripts without changing anything else.
"""

from __future__ import annotations

import io
import logging
import os
from typing import Any

import torch
from PIL import Image


logger = logging.getLogger(__name__)

DEFAULT_MODEL_ID = os.environ.get("UI2CODEN_MODEL_ID", "zai-org/UI2Code_N")


_GEN_PROMPT = (
    "You are generating code for an industrial HMI screen. "
    "Look at the screenshot and produce a single self-contained HTML page "
    "with inline CSS that reproduces the layout, typography, color palette "
    "and interactive elements. Use semantic HTML. No external assets."
)

_REFINE_PROMPT = (
    "This is an industrial HMI reference. The attached HTML is a previous "
    "attempt. Improve the HTML so that its rendered appearance is closer to "
    "the reference: tighten spacing, correct typography hierarchy, align "
    "blocks, preserve the color palette. Return the full updated HTML."
)

_EDIT_PROMPT_TEMPLATE = (
    "The attached HTML represents an industrial HMI screen. Apply this "
    "instruction and return the full updated HTML, nothing else. "
    "Instruction: {instruction}"
)


def _pil_from_bytes(image_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


class UI2CodeModel:
    """Thin wrapper that exposes ``generate``, ``refine`` and ``edit``."""

    name = "ui2coden-9b-4bit"

    def __init__(self, model_id: str = DEFAULT_MODEL_ID, max_new_tokens: int = 4096):
        self.model_id = model_id
        self.max_new_tokens = max_new_tokens
        logger.info("loading %s (this may take several minutes on first run)", model_id)

        from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig

        quant = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

        self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
        self.model = AutoModelForImageTextToText.from_pretrained(
            model_id,
            quantization_config=quant,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )
        self.model.eval()
        logger.info("model loaded: %s", model_id)

    # ------------------------------------------------------------------ core

    def _chat(self, image: Image.Image | None, text: str) -> str:
        content: list[dict[str, Any]] = []
        if image is not None:
            content.append({"type": "image", "image": image})
        content.append({"type": "text", "text": text})

        messages = [{"role": "user", "content": content}]

        inputs = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device)

        with torch.inference_mode():
            generated = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                temperature=0.0,
            )

        prompt_len = inputs["input_ids"].shape[1]
        raw = self.processor.decode(generated[0][prompt_len:], skip_special_tokens=True)
        return self._clean_html(raw)

    # ------------------------------------------------------------------ api

    def generate(self, image_bytes: bytes, frame_name: str = "Untitled", **_: Any) -> str:
        image = _pil_from_bytes(image_bytes)
        prompt = _GEN_PROMPT + f"\nScreen name hint: {frame_name}"
        return self._chat(image, prompt)

    def refine(self, reference_bytes: bytes, current_code: str, **_: Any) -> str:
        image = _pil_from_bytes(reference_bytes)
        prompt = _REFINE_PROMPT + "\n\n<previous_html>\n" + current_code + "\n</previous_html>"
        return self._chat(image, prompt)

    def edit(self, current_code: str, instruction: str, **_: Any) -> str:
        prompt = _EDIT_PROMPT_TEMPLATE.format(instruction=instruction)
        prompt += "\n\n<current_html>\n" + current_code + "\n</current_html>"
        return self._chat(None, prompt)

    # ------------------------------------------------------------------ util

    @staticmethod
    def _clean_html(text: str) -> str:
        """Strip chat markers and isolate the HTML document if present."""
        stripped = text.strip()
        if "```html" in stripped:
            stripped = stripped.split("```html", 1)[1]
            if "```" in stripped:
                stripped = stripped.split("```", 1)[0]
        elif stripped.startswith("```"):
            stripped = stripped.strip("`")
        return stripped.strip()
