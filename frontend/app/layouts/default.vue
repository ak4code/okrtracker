<script setup lang="ts">
const route = useRoute()
const auth = useAuth()

const labels: Record<string, string> = {
  '': 'Дашборд',
  okrs: 'OKR',
  analytics: 'Аналитика',
  admin: 'Администрирование',
  users: 'Пользователи',
  settings: 'Настройки',
  login: 'Авторизация',
  new: 'Создать OKR',
  my: 'Мои OKR',
  team: 'OKR команд',
}

const pageTitle = computed(() => {
  if (typeof route.meta.title === 'string' && route.meta.title) {
    return route.meta.title
  }

  const segments = route.path.split('/').filter(Boolean)
  if (!segments.length) {
    return labels['']
  }

  return labels[segments.at(-1) || ''] || segments.at(-1) || labels['']
})

useHead(() => ({
  title: `${pageTitle.value} · OKR Tracker`,
}))
</script>

<template>
  <div v-if="route.path === '/login'" class="min-h-screen">
    <slot />
  </div>

  <div v-else class="h-screen overflow-hidden bg-ink-50">
    <div class="flex h-full">
      <AppSidebar />

      <main class="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
        <AppHeader :title="pageTitle" />
        <div v-if="!auth.isReady" class="flex min-h-0 flex-1 items-center justify-center p-6">
          <div class="block-radius border border-ink-200 bg-white px-4 py-3 text-sm text-ink-500 shadow-sm">
            Загружаем рабочее пространство...
          </div>
        </div>
        <div v-else class="min-h-0 min-w-0 flex-1 overflow-y-auto overflow-x-hidden p-6">
          <div class="min-w-0 w-full">
            <slot />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>
