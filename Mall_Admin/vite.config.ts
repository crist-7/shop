import { defineConfig, type Plugin } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import viteCompression from 'vite-plugin-compression'

// ============================================================
// Vite 生产环境优化配置 - 商城后台管理系统
// 优化目标：首屏加载速度、构建产物体积、缓存策略
// ============================================================

export default defineConfig(({ mode }) => {
  // 判断是否为生产环境
  const isProduction = mode === 'production'

  // 插件列表
  const plugins: Plugin[] = [vue()]

  // 生产环境：添加 Gzip 压缩插件
  if (isProduction) {
    plugins.push(
      viteCompression({
        algorithm: 'gzip',
        threshold: 1024,
        deleteOriginFile: false,
      })
    )
  }

  return {
    plugins,

    // ============================================================
    // 路径别名配置
    // ============================================================
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },

    // ============================================================
    // 开发服务器配置
    // ============================================================
    server: {
      port: 5174,
      open: true,
      // 代理配置：解决开发环境跨域问题
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        }
      }
    },

    // ============================================================
    // 构建优化配置（核心）
    // ============================================================
    build: {
      target: 'es2020',
      outDir: 'dist',
      assetsDir: 'assets',

      // 小于 4KB 的资源转 Base64 内联
      assetsInlineLimit: 4096,

      cssCodeSplit: true,
      sourcemap: false,
      chunkSizeWarningLimit: 500,

      rollupOptions: {
        output: {
          entryFileNames: 'assets/js/[name]-[hash].js',
          chunkFileNames: 'assets/js/[name]-[hash].js',
          assetFileNames: (assetInfo) => {
            if (assetInfo.name?.endsWith('.css')) {
              return 'assets/css/[name]-[hash][extname]'
            }
            if (/\.(png|jpe?g|gif|svg|webp|ico)$/i.test(assetInfo.name || '')) {
              return 'assets/images/[name]-[hash][extname]'
            }
            if (/\.(woff2?|eot|ttf|otf)$/i.test(assetInfo.name || '')) {
              return 'assets/fonts/[name]-[hash][extname]'
            }
            return 'assets/[name]-[hash][extname]'
          },

          // ============================================================
          // 手动分包策略（后台特有：ECharts 单独打包）
          // ============================================================
          manualChunks: (id) => {
            if (id.includes('node_modules')) {
              // ECharts 图表库（后台独有，体积大，必须单独打包）
              if (id.includes('echarts') || id.includes('zrender')) {
                return 'echarts'
              }

              // Element Plus UI 组件库（需放在 vue 判断之前）
              if (id.includes('element-plus') || id.includes('@element-plus/icons-vue')) {
                return 'element-plus'
              }

              // Vue 核心全家桶
              if (id.includes('vue/dist') || id.includes('pinia') || id.includes('vue-router')) {
                return 'vue-vendor'
              }

              // Axios
              if (id.includes('axios')) {
                return 'axios'
              }

              return 'vendor'
            }
          },
        },
      },

      esbuild: {
        drop: isProduction ? ['console', 'debugger'] : [],
        minify: true,
        target: 'es2020',
      },

      cssMinify: isProduction,
    },

    // ============================================================
    // 依赖预构建优化
    // ============================================================
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'pinia',
        'axios',
        'element-plus',
        '@element-plus/icons-vue',
        'echarts',
      ],
    },
  }
})
