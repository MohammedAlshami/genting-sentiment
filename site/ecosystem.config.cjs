module.exports = {
  apps: [
    {
      name: "genting-sentiment",
      script: "node_modules/vite/bin/vite.js",
      args: "dev --port 3100 --host 0.0.0.0",
      cwd: "/home/shami/projects/genting/site",
      env: { NODE_ENV: "development" },
      instances: 1,
      autorestart: true,
    },
  ],
};
