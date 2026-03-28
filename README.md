# RealRestorer (Pinokio)

Pinokio launcher for [RealRestorer](https://github.com/yfyang007/RealRestorer): generalizable real-world image restoration using the upstream **patched `diffusers`** checkout and a small **Gradio** UI in `ui.py`.

## What you get

- **Install**: PyTorch (via `torch.js`), clone `yfyang007/RealRestorer` into `app/RealRestorer`, editable-install `diffusers`, then the RealRestorer package and UI dependencies.
- **Start**: Gradio on `127.0.0.1` at the next free port (`{{port}}` in `start.js`). Use **Open Web UI** in Pinokio when the URL is captured.
- **Inference-only**: RealIR-Bench is not installed.

## Usage (Pinokio)

1. **Install** — wait for the import check: `RealRestorerPipeline`.
2. **Start** — open the Gradio URL, upload an image, choose or edit the prompt, then **Restore**.
3. Outputs are written under `outputs/` at the project root.

### Recommended inference settings (defaults in UI)

| Setting        | Value   |
|----------------|---------|
| Device         | CUDA    |
| Torch dtype    | bfloat16 when supported |
| Steps          | 28      |
| Guidance scale | 3.0     |
| Seed           | 42      |
| Size level     | 1024    |

Enable **Model CPU offload** if you are tight on VRAM (slower).

## Troubleshooting

- **First run is slow**: the model `RealRestorer/RealRestorer` is downloaded from Hugging Face into the HF cache (often `~/.cache/huggingface` or `%USERPROFILE%\.cache\huggingface` on Windows).
- **VRAM**: use CPU offload, close other GPU apps, or reduce `size_level` if the pipeline supports it.
- **CUDA**: For practical speed, use an NVIDIA GPU with a CUDA build of PyTorch (see `torch.js`).
- **Reset** removes the `env` venv and the `app/RealRestorer` clone; **Install** again to recreate.

## Upstream references

- Paper: [arXiv:2603.25502](https://arxiv.org/abs/2603.25502)
- Code: [yfyang007/RealRestorer](https://github.com/yfyang007/RealRestorer)
- Model: [RealRestorer/RealRestorer](https://huggingface.co/RealRestorer/RealRestorer)

## License and disclaimer

Launcher scripts in this repository are provided for convenience. The **RealRestorer model and benchmark assets** are intended for **non-commercial academic research** per upstream terms; the upstream **code** is intended under **Apache-2.0**. Third-party models and libraries keep their own licenses—comply with all of them when using this project.
