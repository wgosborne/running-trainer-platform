import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/plans': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/runs': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/import': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/strava': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
