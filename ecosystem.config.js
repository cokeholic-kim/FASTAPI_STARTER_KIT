module.exports = {
  apps: [
    {
      name: 'fastapi-api',
      script: 'uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000',
      instances: 'max',
      exec_mode: 'cluster',
      env: {
        ENVIRONMENT: 'development',
      },
      env_production: {
        ENVIRONMENT: 'production',
      },
      error_file: './logs/error.log',
      out_file: './logs/out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      watch: ['app'],
      ignore_watch: ['node_modules', '.git', 'logs', '.pytest_cache', '__pycache__'],
      restart_delay: 4000,
      max_memory_restart: '500M',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
    },
  ],
};
