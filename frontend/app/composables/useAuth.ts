interface LoginPayload {
  email: string
  password: string
}

interface AuthUser {
  id: number
  email: string
  first_name: string
  last_name: string
  is_staff: boolean
  is_superuser: boolean
}

interface TokenPair {
  access: string
  refresh: string
}

let refreshRequest: Promise<void> | null = null
let refreshTimeout: ReturnType<typeof setTimeout> | null = null

const ACCESS_TOKEN_MAX_AGE = 60 * 30
const REFRESH_TOKEN_MAX_AGE = 60 * 60 * 24 * 7

const decodeJwtPayload = (token: string) => {
  const [, payload] = token.split('.')
  if (!payload || !import.meta.client) {
    return null
  }

  try {
    const normalizedPayload = payload.replace(/-/g, '+').replace(/_/g, '/')
    const decodedPayload = atob(normalizedPayload.padEnd(Math.ceil(normalizedPayload.length / 4) * 4, '='))
    return JSON.parse(decodedPayload) as { exp?: number }
  }
  catch {
    return null
  }
}

export const useAuth = () => {
  const config = useRuntimeConfig()
  const accessToken = useCookie<string | null>('okr-access-token', {
    default: () => null,
    maxAge: ACCESS_TOKEN_MAX_AGE,
    sameSite: 'lax',
  })
  const refreshToken = useCookie<string | null>('okr-refresh-token', {
    default: () => null,
    maxAge: REFRESH_TOKEN_MAX_AGE,
    sameSite: 'lax',
  })
  const currentUser = useState<AuthUser | null>('auth-user', () => null)
  const isReady = useState('auth-ready', () => false)
  const isLoading = useState('auth-loading', () => false)

  const isAuthenticated = computed(() => Boolean(accessToken.value && currentUser.value))

  const clearRefreshTimeout = () => {
    if (!refreshTimeout) {
      return
    }

    clearTimeout(refreshTimeout)
    refreshTimeout = null
  }

  const scheduleRefresh = () => {
    clearRefreshTimeout()

    if (!accessToken.value || !import.meta.client) {
      return
    }

    const payload = decodeJwtPayload(accessToken.value)
    if (!payload?.exp) {
      return
    }

    const refreshInMs = Math.max(payload.exp * 1000 - Date.now() - 60_000, 5_000)
    refreshTimeout = window.setTimeout(async () => {
      try {
        await refreshAccessToken()
      }
      catch {
        clearAuth()
      }
    }, refreshInMs)
  }

  const storeTokens = (tokens: TokenPair) => {
    accessToken.value = tokens.access
    refreshToken.value = tokens.refresh
    scheduleRefresh()
  }

  const clearAuth = () => {
    accessToken.value = null
    refreshToken.value = null
    currentUser.value = null
    clearRefreshTimeout()
  }

  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      clearAuth()
      throw new Error('Отсутствует refresh-токен.')
    }

    if (!refreshRequest) {
      refreshRequest = (async () => {
        const response = await $fetch<{ access: string }>(`${config.public.apiBase}/core/auth/jwt/refresh/`, {
          method: 'POST',
          body: {
            refresh: refreshToken.value,
          },
        })

        accessToken.value = response.access
        scheduleRefresh()
      })().finally(() => {
        refreshRequest = null
      })
    }

    await refreshRequest
  }

  const apiFetch = async <T>(path: string, options: Parameters<typeof $fetch<T>>[1] = {}, retry = true) => {
    const headers = new Headers(options?.headers || {})

    if (accessToken.value) {
      headers.set('Authorization', `Bearer ${accessToken.value}`)
    }

    try {
      return await $fetch<T>(`${config.public.apiBase}${path}`, {
        ...options,
        headers,
      })
    }
    catch (error: any) {
      if (error?.response?.status === 401 && retry && refreshToken.value) {
        await refreshAccessToken()
        return apiFetch<T>(path, options, false)
      }

      throw error
    }
  }

  const fetchCurrentUser = async () => {
    currentUser.value = await apiFetch<AuthUser>('/core/auth/me/', {
      method: 'GET',
    })
    scheduleRefresh()
    return currentUser.value
  }

  const login = async (payload: LoginPayload) => {
    isLoading.value = true

    try {
      const tokens = await $fetch<TokenPair>(`${config.public.apiBase}/core/auth/jwt/login/`, {
        method: 'POST',
        body: payload,
      })

      storeTokens(tokens)
      await fetchCurrentUser()
      isReady.value = true
    }
    finally {
      isLoading.value = false
    }
  }

  const initializeAuth = async () => {
    if (isReady.value || import.meta.server) {
      return
    }

    if (!accessToken.value && !refreshToken.value) {
      currentUser.value = null
      isReady.value = true
      return
    }

    isLoading.value = true

    try {
      if (!accessToken.value && refreshToken.value) {
        await refreshAccessToken()
      }

      await fetchCurrentUser()
    }
    catch {
      clearAuth()
    }
    finally {
      isReady.value = true
      isLoading.value = false
    }
  }

  const logout = async () => {
    clearAuth()
    isReady.value = true
    await navigateTo('/login')
  }

  return {
    accessToken,
    apiFetch,
    currentUser,
    fetchCurrentUser,
    initializeAuth,
    isAuthenticated,
    isLoading,
    isReady,
    login,
    logout,
  }
}
