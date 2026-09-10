module.exports = {
  run: [
    {
      method: "shell.run",
      params: {
        message: "git pull",
      },
    },
    {
      when: "{{exists('app/RealRestorer')}}",
      method: "shell.run",
      params: {
        path: "app/RealRestorer",
        message: ["git pull"],
      },
    },
    {
      when: "{{exists('env') && exists('app/RealRestorer/diffusers')}}",
      method: "shell.run",
      params: {
        venv: "../../../env",
        path: "app/RealRestorer/diffusers",
        message: ["uv pip install -e ."],
      },
    },
    {
      when: "{{exists('env') && exists('app/RealRestorer')}}",
      method: "shell.run",
      params: {
        venv: "../../env",
        path: "app/RealRestorer",
        message: ["uv pip install -r requirements.txt", "uv pip install -e ."],
      },
    },
    {
      when: "{{exists('env')}}",
      method: "shell.run",
      params: {
        venv: "env",
        message: ["uv pip install -r requirements.txt"],
      },
    },
    {
      when: "{{exists('env')}}",
      method: "shell.run",
      params: {
        venv: "env",
        message: [
          "uv pip install --force-reinstall transformers==4.57.3 tokenizers==0.22.1 qwen-vl-utils==0.0.10 huggingface-hub==0.36.2",
        ],
      },
    },
    {
      // The upstream requirements can pull a generic (CPU) torch wheel over the
      // platform build installed at install time, so re-assert torch last.
      when: "{{exists('env')}}",
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          path: ".",
          venv: "env",
        },
      },
    },
  ],
}
