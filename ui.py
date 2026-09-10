"""
Gradio UI for RealRestorer inference (Pinokio launcher).
"""
from __future__ import annotations

import argparse
import gc
import random
import threading
import time
from pathlib import Path

import gradio as gr
import torch
from PIL import Image

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_SEED = 2**31 - 1

PIPE = None
PIPE_KWARGS: dict = {}
# The pipeline is a single shared, stateful object: serialize loads and calls.
PIPE_LOCK = threading.Lock()

PRESETS: list[tuple[str, str]] = [
    ("Blur removal", "Please deblur the image and make it sharper"),
    ("Compression artifacts", "Please restore the image clarity and artifacts."),
    ("Lens flare", "Please remove the lens flare and glare from the image."),
    ("Moiré", "Please remove the moiré patterns from the image"),
    ("Dehazing", "Please dehaze the image"),
    ("Low-light", "Please restore this low-quality image, recovering its normal brightness and clarity."),
    ("Denoising", "Please remove noise from the image."),
    ("Rain", "Please remove the rain from the image and restore its clarity."),
    ("Reflection", "Please remove the reflection from the image."),
]


def _dtype_for_device(use_cuda: bool):
    if use_cuda and torch.cuda.is_available():
        if torch.cuda.is_bf16_supported():
            return torch.bfloat16
        return torch.float16
    return torch.float32


def _release_pipe():
    """Drop the cached pipeline and give its VRAM back."""
    global PIPE, PIPE_KWARGS
    PIPE = None
    PIPE_KWARGS = {}
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def get_pipe(use_cuda: bool, cpu_offload: bool):
    global PIPE, PIPE_KWARGS
    want = {"use_cuda": use_cuda, "cpu_offload": cpu_offload}
    if PIPE is not None and PIPE_KWARGS == want:
        return PIPE

    # A pipeline built for a different device/offload mode is still holding
    # memory; free it before loading the replacement.
    if PIPE is not None:
        _release_pipe()

    from diffusers import RealRestorerPipeline

    dtype = _dtype_for_device(use_cuda)
    pipe = RealRestorerPipeline.from_pretrained(
        "RealRestorer/RealRestorer",
        torch_dtype=dtype,
    )
    if use_cuda and torch.cuda.is_available():
        if cpu_offload:
            pipe.enable_model_cpu_offload()
        else:
            pipe.to("cuda")
    else:
        pipe.to("cpu")

    PIPE = pipe
    PIPE_KWARGS = want.copy()
    return PIPE


def _resolve_seed(seed) -> int:
    """Coerce the seed box (which can be blank, float or negative) to an int."""
    try:
        seed_i = int(seed)
    except (TypeError, ValueError):
        return random.randint(0, MAX_SEED)
    if seed_i < 0:
        return random.randint(0, MAX_SEED)
    return seed_i % (MAX_SEED + 1)


def _int_or(value, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _float_or(value, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _first_image(result):
    images = getattr(result, "images", None)
    if images is None and isinstance(result, (list, tuple)):
        images = result
    if not images:
        return None
    return images[0]


def run_restore(
    image: Image.Image | None,
    prompt: str,
    negative_prompt: str,
    num_inference_steps: float,
    guidance_scale: float,
    seed: float,
    size_level: float,
    use_cuda: bool,
    cpu_offload: bool,
):
    if image is None:
        return None, "Upload an image first."

    prompt = (prompt or "").strip()
    if not prompt:
        return None, "Enter a prompt (or pick a preset)."

    if use_cuda and not torch.cuda.is_available():
        return (
            None,
            "CUDA was requested but is not available. Uncheck “Use CUDA” or install a CUDA build of PyTorch.",
        )

    pil = image.convert("RGB")
    seed_i = _resolve_seed(seed)
    steps = max(1, _int_or(num_inference_steps, 28))
    size_i = max(64, _int_or(size_level, 1024))

    with PIPE_LOCK:
        try:
            pipe = get_pipe(use_cuda=use_cuda, cpu_offload=cpu_offload)
        except Exception as e:
            # Never leave a half-built pipeline cached.
            _release_pipe()
            return None, f"Failed to load model: {e}"

        try:
            result = pipe(
                image=pil,
                prompt=prompt,
                negative_prompt=(negative_prompt or "").strip(),
                num_inference_steps=steps,
                guidance_scale=_float_or(guidance_scale, 3.0),
                seed=seed_i,
                size_level=size_i,
            )
        except Exception as e:
            return None, f"Inference failed: {e}"

    out = _first_image(result)
    if out is None:
        return None, "Inference returned no image."

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_path = OUTPUT_DIR / f"realrestorer_{stamp}_{seed_i}.png"
    try:
        out.save(out_path)
    except OSError as e:
        return out, f"Restored, but saving to {out_path} failed: {e}"
    return out, f"Saved to {out_path} (seed {seed_i})"


def apply_preset(key: str):
    for label, text in PRESETS:
        if label == key:
            return gr.update(value=text)
    return gr.update()


def build_ui():
    preset_choices = [p[0] for p in PRESETS]
    with gr.Blocks(title="RealRestorer") as demo:
        gr.Markdown("# RealRestorer")
        gr.Markdown(
            "Generalizable real-world image restoration. "
            "First run downloads weights from Hugging Face (large). "
            "Recommended: CUDA, bfloat16, and enough VRAM or CPU offload."
        )

        with gr.Row():
            with gr.Column():
                input_image = gr.Image(type="pil", label="Input image")
                preset = gr.Dropdown(
                    label="Example prompts",
                    choices=preset_choices,
                    value=None,
                )
                prompt = gr.Textbox(
                    label="Prompt",
                    lines=3,
                    value="Please deblur the image and make it sharper",
                )
                negative_prompt = gr.Textbox(label="Negative prompt", lines=2, value="")
                with gr.Row():
                    num_inference_steps = gr.Slider(1, 50, value=28, step=1, label="Inference steps")
                    guidance_scale = gr.Slider(0.0, 15.0, value=3.0, step=0.5, label="Guidance scale")
                with gr.Row():
                    seed = gr.Number(value=42, label="Seed (-1 = random)", precision=0)
                    size_level = gr.Slider(256, 2048, value=1024, step=64, label="Size level")
                use_cuda = gr.Checkbox(value=torch.cuda.is_available(), label="Use CUDA (recommended)")
                cpu_offload = gr.Checkbox(value=True, label="Model CPU offload (saves VRAM, slower)")
                run_btn = gr.Button("Restore", variant="primary")

            with gr.Column():
                output_image = gr.Image(type="pil", label="Output")
                status = gr.Textbox(label="Status", interactive=False)

        preset.change(fn=apply_preset, inputs=[preset], outputs=[prompt])

        run_btn.click(
            fn=run_restore,
            inputs=[
                input_image,
                prompt,
                negative_prompt,
                num_inference_steps,
                guidance_scale,
                seed,
                size_level,
                use_cuda,
                cpu_offload,
            ],
            outputs=[output_image, status],
        )

    return demo


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()

    demo = build_ui()
    demo.launch(server_name=args.host, server_port=args.port, share=False, inbrowser=False)
