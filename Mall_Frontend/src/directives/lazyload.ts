/**
 * 图片懒加载指令
 *
 * 使用 Intersection Observer API 实现高性能懒加载
 * 支持占位图、加载失败回退、加载动画
 */

// 默认占位图（1x1 透明像素）
const DEFAULT_PLACEHOLDER =
  'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'

// 加载状态缓存，避免重复加载
const loadingSet = new WeakSet<HTMLImageElement>()
const loadedSet = new WeakSet<HTMLImageElement>()

// Intersection Observer 实例（复用）
let observer: IntersectionObserver | null = null

/**
 * 获取或创建 Observer 实例
 */
function getObserver(): IntersectionObserver {
  if (observer) return observer

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        // 元素进入视口
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement
          const src = img.dataset.lazySrc

          if (src && !loadingSet.has(img) && !loadedSet.has(img)) {
            loadImage(img, src)
          }
        }
      })
    },
    {
      rootMargin: '100px 0px', // 提前 100px 开始加载
      threshold: 0.01, // 1% 可见即触发
    }
  )

  return observer
}

/**
 * 加载图片
 */
function loadImage(img: HTMLImageElement, src: string) {
  if (loadingSet.has(img)) return

  loadingSet.add(img)

  // 创建临时图片预加载
  const tempImg = new Image()

  tempImg.onload = () => {
    img.src = src
    img.classList.remove('lazy-loading')
    img.classList.add('lazy-loaded')
    loadedSet.add(img)
    loadingSet.delete(img)

    // 停止观察
    getObserver().unobserve(img)
  }

  tempImg.onerror = () => {
    img.classList.remove('lazy-loading')
    img.classList.add('lazy-error')
    loadingSet.delete(img)

    // 设置失败占位图
    img.src = img.dataset.lazyError || DEFAULT_PLACEHOLDER
  }

  tempImg.src = src
}

/**
 * 懒加载指令
 */
export const lazyLoadDirective = {
  mounted(el: HTMLImageElement, binding: { value: string }) {
    const src = binding.value

    if (!src) {
      el.src = DEFAULT_PLACEHOLDER
      return
    }

    // 存储真实 src
    el.dataset.lazySrc = src

    // 设置占位图
    el.src = el.dataset.lazyPlaceholder || DEFAULT_PLACEHOLDER

    // 添加加载中样式
    el.classList.add('lazy-loading')

    // 开始观察
    getObserver().observe(el)
  },

  updated(el: HTMLImageElement, binding: { value: string; oldValue: string }) {
    const src = binding.value

    // src 变化时更新
    if (src !== binding.oldValue) {
      el.dataset.lazySrc = src

      // 如果元素在视口内，立即加载
      const rect = el.getBoundingClientRect()
      const inViewport =
        rect.top < window.innerHeight + 100 &&
        rect.bottom > -100

      if (inViewport) {
        loadImage(el, src)
      }
    }
  },

  beforeUnmount(el: HTMLImageElement) {
    getObserver().unobserve(el)
  },
}

/**
 * 注册全局指令
 */
export function setupLazyLoad(app: any) {
  app.directive('lazy', lazyLoadDirective)
}

// 默认导出
export default lazyLoadDirective
