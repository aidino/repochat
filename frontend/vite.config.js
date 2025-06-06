import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],
    
    // Path resolution
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '@components': resolve(__dirname, 'src/components'),
        '@services': resolve(__dirname, 'src/services'),
        '@composables': resolve(__dirname, 'src/composables'),
        '@config': resolve(__dirname, 'src/config'),
        '@utils': resolve(__dirname, 'src/utils'),
        '@assets': resolve(__dirname, 'src/assets'),
        '@styles': resolve(__dirname, 'src/styles')
      }
    },

    // Environment variables
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0')
    },

    // Development server configuration
    server: {
      port: 3000,
      host: true,
      cors: true,
      proxy: {
        // Proxy API requests to backend during development
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          configure: (proxy, options) => {
            // Log proxy requests in development
            proxy.on('error', (err, req, res) => {
              console.log('🔥 Proxy error:', err)
            })
            proxy.on('proxyReq', (proxyReq, req, res) => {
              console.log('📤 Proxy request:', req.method, req.url)
            })
            proxy.on('proxyRes', (proxyRes, req, res) => {
              console.log('📥 Proxy response:', proxyRes.statusCode, req.url)
            })
          }
        }
      }
    },

    // Build configuration
    build: {
      outDir: 'dist',
      sourcemap: mode === 'development',
      minify: mode === 'production',
      
      // Rollup options
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['vue'],
            api: ['axios'],
            utils: ['@vueuse/core']
          }
        }
      },

      // Optimize deps
      optimizeDeps: {
        include: ['vue', 'axios', '@vueuse/core']
      }
    },

    // Environment variables prefix
    envPrefix: 'VITE_',

    // CSS configuration
    css: {
      devSourcemap: mode === 'development'
    }
  }
}) 