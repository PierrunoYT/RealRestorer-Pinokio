module.exports = {
  run: [
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          path: "app",
          venv: "env",
        },
      },
    },
    {
      when: "{{!exists('app/RealRestorer')}}",
      method: "shell.run",
      params: {
        venv: "env",
        message: [
          "git clone https://github.com/yfyang007/RealRestorer.git app/RealRestorer",
        ],
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
      method: "shell.run",
      params: {
        venv: "env",
        path: "app/RealRestorer/diffusers",
        message: ["uv pip install -e ."],
      },
    },
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app/RealRestorer",
        message: ["uv pip install -r requirements.txt", "uv pip install -e ."],
      },
    },
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: ["uv pip install -r requirements.txt"],
      },
    },
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: [
          "python -c \"from diffusers import RealRestorerPipeline; print(RealRestorerPipeline.__name__)\"",
        ],
      },
    },
    {
      method: "fs.write",
      params: {
        path: "INSTALLATION_COMPLETE.txt",
        text:
          "RealRestorer installation completed.\n\n" +
          "Next: Start the app and open the Gradio URL.\n" +
          "First inference downloads model weights from Hugging Face.\n\n" +
          "Upstream: https://github.com/yfyang007/RealRestorer\n" +
          "Paper: https://arxiv.org/abs/2603.25502\n",
      },
    },
  ],
}
