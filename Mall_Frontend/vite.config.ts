import { defineConfig, type Plugin } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import viteCompression from 'vite-plugin-compression'

// ============================================================
// Vite 生产环境优化配置
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
        // 压缩算法：gzip 兼容性最好，brotli 压缩率更高
        algorithm: 'gzip',
        // 大于 1KB 的文件才压缩
        threshold: 1024,
        // 压缩后删除原文件（Nginx 需配置 gzip_static on）
        deleteOriginFile: false,
      })
    )
    // 可选：同时生成 Brotli 压缩（压缩率更高，但兼容性稍差）
    // plugins.push(
    //   viteCompression({
    //     algorithm: 'brotliCompress',
    //     threshold: 1024,
    //     deleteOriginFile: false,
    //   })
    // )
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
      port: 5173,
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
      // 目标浏览器：现代浏览器，支持原生 ES 模块
      target: 'es2020',

      // 输出目录
      outDir: 'dist',

      // 静态资源处理
      assetsDir: 'assets',

      // 小于 4KB 的资源转 Base64 内联
      // 原理：减少 HTTP 请求数，但会增加 JS 体积
      // 建议：4KB 是平衡点，太小不值得请求，太大内联会增体积
      assetsInlineLimit: 4096,

      // 启用 CSS 代码分割
      // 原理：每个页面的 CSS 单独打包，实现按需加载
      cssCodeSplit: true,

      // 构建后是否生成 source map（生产环境关闭以减小体积）
      sourcemap: false,

      // chunk 大小警告阈值（单位：KB）
      chunkSizeWarningLimit: 500,

      // ============================================================
      // Rollup 打包配置（分包策略核心）
      // ============================================================
      rollupOptions: {
        output: {
          // 入口文件命名
          entryFileNames: 'assets/js/[name]-[hash].js',

          // 代码块命名
          chunkFileNames: 'assets/js/[name]-[hash].js',

          // 静态资源命名
          assetFileNames: (assetInfo) => {
            // CSS 文件单独目录
            if (assetInfo.name?.endsWith('.css')) {
              return 'assets/css/[name]-[hash][extname]'
            }
            // 图片资源
            if (/\.(png|jpe?g|gif|svg|webp|ico)$/i.test(assetInfo.name || '')) {
              return 'assets/images/[name]-[hash][extname]'
            }
            // 字体文件
            if (/\.(woff2?|eot|ttf|otf)$/i.test(assetInfo.name || '')) {
              return 'assets/fonts/[name]-[hash][extname]'
            }
            // 其他资源
            return 'assets/[name]-[hash][extname]'
          },

          // ============================================================
          // 手动分包策略（Chunk Splitting）
          // 原理：将稳定的第三方库单独打包，利用浏览器缓存
          // 用户更新业务代码时，无需重新下载这些不变的依赖
          // ============================================================
          manualChunks: (id) => {
            // node_modules 中的依赖
            if (id.includes('node_modules')) {
              // Element Plus UI 组件库（体积大，单独打包，需放在 vue 判断之前）
              if (id.includes('element-plus') || id.includes('@element-plus/icons-vue')) {
                return 'element-plus'
              }

              // Vue 核心全家桶（变化少，单独打包）
              if (id.includes('vue/dist') || id.includes('pinia') || id.includes('vue-router')) {
                return 'vue-vendor'
              }

              // Axios 网络请求库
              if (id.includes('axios')) {
                return 'axios'
              }

              // 其他第三方库合并为一个包
              return 'vendor'
            }
          },
        },
      },

      // ============================================================
      // esbuild 配置（编译优化）
      // ============================================================
      esbuild: {
        // 生产环境移除 console.log 和 debugger
        // 原理：减少代码体积，避免生产环境输出调试信息
        drop: isProduction ? ['console', 'debugger'] : [],
        // 开启压缩
        minify: true,
        // 目标环境
        target: 'es2020',
      },

      // ============================================================
      // CSS 相关配置
      // ============================================================
      cssMinify: isProduction,
    },

    // ============================================================
    // 依赖预构建优化
    // 原理：将依赖预打包，减少开发环境启动时间
    // ============================================================
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'pinia',
        'axios',
        'element-plus',
        '@element-plus/icons-vue',
      ],
    },
  }
})
