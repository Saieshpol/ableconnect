import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  if (mode === 'production' && !env.VITE_API_URL) {
    throw new Error('VITE_API_URL must point to the hosted FastAPI backend for production builds.')
  }

  return {
    plugins: [react(), tailwindcss()],
    server: { port: 5173, host: true },
  }
})
