export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) {
    return
  }

  const auth = useAuth()

  await auth.initializeAuth()

  if (to.path === '/login' && auth.isAuthenticated.value) {
    return navigateTo('/')
  }

  if (to.path !== '/login' && !auth.isAuthenticated.value) {
    return navigateTo('/login')
  }
})
