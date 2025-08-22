import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'


// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),tailwindcss()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    }
  },
  build: {
    chunkSizeWarningLimit: 1500, // raise from 500 KB to 1.5 MB
  },
})
