import path from 'path'
import { fileURLToPath } from 'url'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig, loadEnv } from 'vite'
import type { PreviewOptions } from 'vite'

const dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, dirname, '')
  const apiProxyTarget = env.DHARA_API_PROXY_TARGET || 'http://127.0.0.1:8001'
  const previewApiProxyTarget = env.DHARA_PREVIEW_API_PROXY_TARGET
  const previewProxy: NonNullable<PreviewOptions['proxy']> = previewApiProxyTarget
    ? { '/api': { target: previewApiProxyTarget, changeOrigin: true } }
    : {}

  return {
    plugins: [react(), tailwindcss()],
    server: {
      proxy: {
        '/api': {
          target: apiProxyTarget,
          changeOrigin: true,
        },
      },
    },
    // Vite preview otherwise inherits server.proxy. Keep the production-like
    // preview independent of the local API unless explicitly opted in.
    preview: {
      proxy: previewProxy,
    },
    resolve: {
      alias: {
        '@': path.resolve(dirname, './src'),
      },
    },
  }
})
