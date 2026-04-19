"""
Wrapper around the real UI2Code^N visual language model.

The model ID is ``zai-org/UI2Code_N``. It is a 9B-parameter VLM built on
GLM-4.1V-9B-Base.

Loading mode is controlled by the ``UI2CODEN_QUANT`` environment variable:

* ``none`` (default) — load full-precision bf16 weights, recommended for
  real measurements on a workstation GPU (e.g. RTX 4090, 24 GB VRAM).
* ``8bit`` — load with 8-bit weights via ``bitsandbytes`` (mid-range GPUs).
* ``4bit`` — load with 4-bit NF4 weights and CPU/RAM offload, used only on
  laptops with very limited VRAM (e.g. RTX 3060 Laptop, 6 GB).

Quantisation is therefore opt-in. By default the wrapper does **not**
quantise the model, because all reported timings and qualitative results
in the thesis must be obtained from the unquantised model.

The class follows the same ``generate / refine / edit`` interface that the
rule-based stand-in exposes, so it can be dropped into the local HTTP
service and evaluation scripts without changing anything else.
"""

from __future__ import annotations

import io
import json
import logging
import os
from typing import Any, Optional

import torch
from PIL import Image


logger = logging.getLogger(__name__)

DEFAULT_MODEL_ID = os.environ.get("UI2CODEN_MODEL_ID", "zai-org/UI2Code_N")
DEFAULT_QUANT = os.environ.get("UI2CODEN_QUANT", "none").lower()


_GEN_PROMPT = (
    "You are generating code for an industrial HMI screen. "
    "Look at the screenshot and produce a single self-contained HTML page "
    "with inline CSS that reproduces the layout, typography, color palette "
    "and interactive elements. Use semantic HTML. No external assets."
)

_REFINE_PROMPT = (
    "This is an industrial HMI reference. The first image is the target "
    "reference. The second image is the current rendered output of the "
    "attached HTML. Improve the HTML so that its rendered appearance is "
    "closer to the reference: tighten spacing, correct typography "
    "hierarchy, align blocks, preserve the color palette, fix obviously "
    "missing elements visible in the reference but absent from the current "
    "render. Return the full updated HTML."
)

_EDIT_PROMPT_TEMPLATE = (
    "The attached HTML represents an industrial HMI screen. Apply this "
    "instruction and return the full updated HTML, nothing else. "
    "Instruction: {instruction}"
)


def _pil_from_bytes(image_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


def _format_context_block(
    css_hints: Optional[dict] = None,
    variables: Optional[dict] = None,
) -> str:
    """Render optional Figma context as a compact, model-readable block.

    The block is appended to the prompt only when at least one of the two
    inputs is provided. Empty dicts are treated as "not provided".
    """
    parts: list[str] = []
    if variables:
        parts.append(
            "<design_variables>\n"
            + json.dumps(variables, ensure_ascii=False, indent=2)
            + "\n</design_variables>"
        )
    if css_hints:
        parts.append(
            "<css_hints>\n"
            + json.dumps(css_hints, ensure_ascii=False, indent=2)
            + "\n</css_hints>"
        )
    return ("\n\n" + "\n\n".join(parts)) if parts else ""


class UI2CodeModel:
    """Thin wrapper that exposes ``generate``, ``refine`` and ``edit``."""

    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_ID,
        max_new_tokens: int = 4096,
        quant: str = DEFAULT_QUANT,
    ):
        self.model_id = model_id
        self.max_new_tokens = max_new_tokens
        self.quant = (quant or "none").lower()
        self.name = f"ui2coden-9b-{self.quant}"
        logger.info(
            "loading %s in quant=%s (this may take several minutes on first run)",
            model_id,
            self.quant,
        )

        from transformers import AutoModelForImageTextToText, AutoProcessor

        kwargs: dict[str, Any] = {
            "torch_dtype": torch.bfloat16,
            "trust_remote_code": True,
        }

        if self.quant == "none":
            if torch.cuda.is_available():
                kwargs["device_map"] = "cuda"
            else:
                kwargs["device_map"] = "auto"
        elif self.quant in {"4bit", "8bit"}:
            from transformers import BitsAndBytesConfig

            if self.quant == "4bit":
                kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.bfloat16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
            else:
                kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
            kwargs["device_map"] = "auto"
        else:
            raise ValueError(
                f"Unsupported UI2CODEN_QUANT={self.quant!r}; expected one of "
                "'none', '8bit', '4bit'."
            )

        self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
        self.model = AutoModelForImageTextToText.from_pretrained(model_id, **kwargs)
        self.model.eval()
        logger.info("model loaded: %s (%s)", model_id, self.name)

    # ------------------------------------------------------------------ core

    def _chat(self, images: list[Image.Image], text: str) -> str:
        content: list[dict[str, Any]] = []
        for image in images:
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

    def generate(
        self,
        image_bytes: bytes,
        frame_name: str = "Untitled",
        css_hints: Optional[dict] = None,
        variables: Optional[dict] = None,
        **_: Any,
    ) -> str:
        image = _pil_from_bytes(image_bytes)
        prompt = _GEN_PROMPT + f"\nScreen name hint: {frame_name}"
        prompt += _format_context_block(css_hints=css_hints, variables=variables)
        return self._chat([image], prompt)

    def refine(
        self,
        reference_bytes: bytes,
        current_code: str,
        rendered_bytes: Optional[bytes] = None,
        css_hints: Optional[dict] = None,
        variables: Optional[dict] = None,
        **_: Any,
    ) -> str:
        images: list[Image.Image] = [_pil_from_bytes(reference_bytes)]
        if rendered_bytes:
            images.append(_pil_from_bytes(rendered_bytes))
            preface = (
                "\n\nFirst image: target reference. "
                "Second image: current render of the attached HTML."
            )
        else:
            preface = (
                "\n\nOnly the reference image was supplied. "
                "Improve the HTML to match it as closely as possible."
            )
        prompt = _REFINE_PROMPT + preface
        prompt += _format_context_block(css_hints=css_hints, variables=variables)
        prompt += "\n\n<previous_html>\n" + current_code + "\n</previous_html>"
        return self._chat(images, prompt)

    def edit(
        self,
        current_code: str,
        instruction: str,
        css_hints: Optional[dict] = None,
        variables: Optional[dict] = None,
        **_: Any,
    ) -> str:
        prompt = _EDIT_PROMPT_TEMPLATE.format(instruction=instruction)
        prompt += _format_context_block(css_hints=css_hints, variables=variables)
        prompt += "\n\n<current_html>\n" + current_code + "\n</current_html>"
        return self._chat([], prompt)

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
