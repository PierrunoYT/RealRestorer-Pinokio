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
        venv: "env",
        path: "app/RealRestorer/diffusers",
        message: ["uv pip install -e ."],
      },
    },
    {
      when: "{{exists('env') && exists('app/RealRestorer')}}",
      method: "shell.run",
      params: {
        venv: "env",
        path: "app/RealRestorer",
        message: ["uv pip install -r requirements.txt", "uv pip install -e ."],
      },
    },
    {
      when: "{{exists('env') && exists('app/RealRestorer')}}",
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: ["uv pip install -r requirements.txt"],
      },
    },
  ],
}
