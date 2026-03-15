<script setup lang="ts">
import { BarChart3, LayoutDashboard, LogOut, Settings, Target } from 'lucide-vue-next'

const route = useRoute()
const auth = useAuth()

const sections = computed(() => [
  { label: 'Дашборд', to: '/', icon: LayoutDashboard },
  { label: 'Все OKR', to: '/okrs', icon: Target },
  { label: 'Аналитика', to: '/analytics', icon: BarChart3 },
  { label: 'Настройки', to: '/settings', icon: Settings },
])

const isActive = (item: { to: string | { path: string, query?: Record<string, string> } }) => {
  if (typeof item.to === 'string') {
    return item.to === '/' ? route.path === item.to : route.path.startsWith(item.to)
  }

  const queryQuarter = typeof route.query.quarter === 'string' ? route.query.quarter : ''
  return route.path === item.to.path && queryQuarter === (item.to.query?.quarter || '')
}

const userInitials = computed(() => {
  const user = auth.currentUser.value
  if (!user) {
    return 'OK'
  }

  const initials = `${user.first_name[0] || ''}${user.last_name[0] || ''}`.trim()
  return initials || user.email.slice(0, 2).toUpperCase()
})

const userFullName = computed(() => {
  const user = auth.currentUser.value
  if (!user) {
    return 'Пользователь'
  }

  return `${user.first_name} ${user.last_name}`.trim() || user.email
})

const userRoleLabel = computed(() => {
  const user = auth.currentUser.value
  if (!user) {
    return 'Нет данных'
  }

  if (user.is_superuser) {
    return 'Администратор'
  }

  if (user.is_staff) {
    return 'Сотрудник'
  }

  return 'Пользователь'
})
</script>

<template>
  <aside class="sticky top-0 hidden h-screen w-64 shrink-0 flex-col justify-between border-r border-ink-200 bg-white lg:flex">
    <div class="flex min-h-0 flex-1 flex-col">
      <div class="flex h-16 items-center border-b border-ink-200 px-6">
        <div class="flex items-center gap-3">
          <div class="block-radius flex h-9 w-9 items-center justify-center bg-gradient-to-br from-sky-500 to-violet-600 text-white">
            <Target class="h-4.5 w-4.5" />
          </div>
          <div>
            <p class="font-display text-lg font-semibold text-ink-900">OKR Tracker</p>
          </div>
        </div>
      </div>

      <nav class="flex-1 space-y-1 px-3 py-4">
        <NuxtLink
          v-for="item in sections"
          :key="typeof item.to === 'string' ? item.to : `${item.to.path}-${item.to.query?.quarter || ''}`"
          :to="item.to"
          class="flex items-center gap-3 rounded-sm px-3 py-2.5 text-sm font-medium transition"
          :class="
            isActive(item)
              ? 'bg-ink-100 text-ink-900'
              : 'text-ink-600 hover:bg-ink-50 hover:text-ink-900'
          "
        >
          <component :is="item.icon" class="h-5 w-5" />
          <span>{{ item.label }}</span>
        </NuxtLink>
      </nav>
    </div>

    <div class="mt-auto border-t border-ink-200 p-4">
      <ClientOnly>
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-sky-400 to-violet-500 text-sm font-semibold text-white">
            {{ userInitials }}
          </div>
          <div class="min-w-0">
            <p class="truncate text-sm font-medium text-ink-900">{{ userFullName }}</p>
            <p class="truncate text-xs text-ink-500">{{ userRoleLabel }}</p>
          </div>
        </div>
        <button
          type="button"
          class="btn btn-secondary mt-4 w-full"
          @click="auth.logout()"
        >
          <LogOut class="h-4 w-4" />
          <span>Выйти</span>
        </button>

        <template #fallback>
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-sky-400 to-violet-500 text-sm font-semibold text-white">
              OK
            </div>
            <div class="min-w-0">
              <p class="truncate text-sm font-medium text-ink-900">Пользователь</p>
              <p class="truncate text-xs text-ink-500">Нет данных</p>
            </div>
          </div>
        </template>
      </ClientOnly>
    </div>
  </aside>
</template>
