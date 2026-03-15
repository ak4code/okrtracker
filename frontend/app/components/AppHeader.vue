<script setup lang="ts">
import { Plus } from 'lucide-vue-next'

const route = useRoute()
const okrApi = useOkrApi()
const dashboardQuarter = useState<string>('dashboard-quarter', () => '')
const { data: quarterOptions } = await useAsyncData(
  'okr-quarters',
  () => okrApi.fetchQuarters(),
  {
    server: false,
    default: () => [],
  },
)

const quarters = computed(() =>
  quarterOptions.value.map((item) => item.name),
)

watchEffect(() => {
  if (!dashboardQuarter.value && quarterOptions.value.length) {
    dashboardQuarter.value = quarterOptions.value.find((item) => item.isActive)?.name || quarterOptions.value[0].name
  }
})

defineProps<{
  title: string
}>()
</script>

<template>
  <header class="relative z-20 flex h-16 shrink-0 items-center justify-between border-b border-ink-200 bg-white px-6">
    <div class="flex items-center gap-4">
      <div>
        <p class="text-sm font-medium text-ink-900">{{ title }}</p>
      </div>
    </div>

    <div class="hidden items-center gap-3 md:flex">
      <div v-if="route.path === '/'" class="flex items-center gap-3">
        <span class="text-sm text-ink-500">Квартал</span>
        <select v-model="dashboardQuarter" class="input-base min-w-36 py-2" :disabled="!quarters.length">
          <option v-for="quarter in quarters" :key="quarter" :value="quarter">{{ quarter }}</option>
        </select>
      </div>
      <NuxtLink to="/okrs/new" class="btn btn-accent">
        <Plus class="h-4 w-4" />
        <span>Создать OKR</span>
      </NuxtLink>
    </div>
  </header>
</template>
