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
        venv: "env",
        path: "app/RealRestorer",
        message: ["git pull"],
      },
    },
    {
      when: "{{exists('env') && exists('app/RealRestorer')}}",
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
      when: "{{exists('env') && exists('app/RealRestorer')}}",
      method: "shell.run",
      params: {
        venv: "env",
        message: ["uv pip install -r requirements.txt"],
      },
    },
    {
      when: "{{exists('env') && exists('app/RealRestorer')}}",
      method: "shell.run",
      params: {
        venv: "env",
        message: [
          "uv pip install --force-reinstall transformers==4.57.3 tokenizers==0.22.1 qwen-vl-utils==0.0.10 huggingface-hub==0.36.2",
        ],
      },
    },
  ],
}
