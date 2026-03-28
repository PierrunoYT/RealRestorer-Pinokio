module.exports = {
  run: [
    {
      when: "{{exists('env')}}",
      method: "fs.rm",
      params: {
        path: "env",
      },
    },
    {
      when: "{{exists('app/env')}}",
      method: "fs.rm",
      params: {
        path: "app/env",
      },
    },
    {
      when: "{{exists('app/RealRestorer/env')}}",
      method: "fs.rm",
      params: {
        path: "app/RealRestorer/env",
      },
    },
    {
      when: "{{exists('app/RealRestorer/diffusers/env')}}",
      method: "fs.rm",
      params: {
        path: "app/RealRestorer/diffusers/env",
      },
    },
    {
      when: "{{exists('app/RealRestorer')}}",
      method: "fs.rm",
      params: {
        path: "app/RealRestorer",
      },
    },
  ],
}
