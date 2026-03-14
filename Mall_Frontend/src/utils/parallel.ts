/**
 * 并行请求工具函数
 * 用于优化无依赖关系的 API 请求，减少 TTFB
 */

import { ref, type Ref } from 'vue'

/**
 * 请求结果类型
 */
export interface ParallelResult<T> {
  data: T | null
  error: Error | null
  loading: Ref<boolean>
}

/**
 * 并行执行多个无依赖关系的 API 请求
 * 使用 Promise.all 实现真正的并行请求
 *
 * @example
 * ```ts
 * const [categories, banners, goods] = await parallelRequest([
 *   () => getCategoryList(),
 *   () => getBannerList(),
 *   () => getGoodsList()
 * ])
 * ```
 */
export async function parallelRequest<T extends any[]>(
  requestFns: { [K in keyof T]: () => Promise<T[K]> }
): Promise<{ [K in keyof T]: T[K] | null }> {
  const promises = requestFns.map((fn) =>
    fn().catch((error) => {
      console.error('并行请求失败:', error)
      return null
    })
  )

  return Promise.all(promises) as Promise<{ [K in keyof T]: T[K] | null }>
}

/**
 * 带加载状态的并行请求 Hook
 * 自动管理 loading 状态
 *
 * @example
 * ```ts
 * const { data, loading, error, execute } = useParallelRequest([
 *   () => getCategoryList(),
 *   () => getBannerList()
 * ])
 *
 * onMounted(execute)
 * ```
 */
export function useParallelRequest<T extends any[]>(
  requestFns: { [K in keyof T]: () => Promise<T[K]> }
) {
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const data = ref<{ [K in keyof T]: T[K] | null } | null>(null)

  const execute = async () => {
    loading.value = true
    error.value = null

    try {
      data.value = await parallelRequest(requestFns)
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  return {
    data,
    loading,
    error,
    execute,
  }
}

/**
 * 带重试的请求
 * 适用于网络不稳定的环境
 *
 * @param requestFn 请求函数
 * @param retries 重试次数
 * @param delay 重试间隔（毫秒）
 */
export async function retryRequest<T>(
  requestFn: () => Promise<T>,
  retries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: Error | null = null

  for (let i = 0; i < retries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      lastError = error as Error
      if (i < retries - 1) {
        await new Promise((resolve) => setTimeout(resolve, delay))
      }
    }
  }

  throw lastError
}

/**
 * 请求竞速
 * 同时发起多个相同功能的请求，返回最快的响应
 * 适用于有备用 API 服务的场景
 */
export async function raceRequest<T>(
  requestFns: (() => Promise<T>)[]
): Promise<T> {
  return Promise.race(requestFns.map((fn) => fn()))
}

export default {
  parallelRequest,
  useParallelRequest,
  retryRequest,
  raceRequest,
}
