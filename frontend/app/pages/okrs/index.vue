<script setup lang="ts">
definePageMeta({
  title: 'Все OKR',
})

import { Plus, RotateCcw } from 'lucide-vue-next'
import { getOkrStatusLabel } from '~/composables/useStatusDisplay'

const route = useRoute()
const okrApi = useOkrApi()
const isHydrated = ref(false)

onMounted(() => {
  isHydrated.value = true
})

const { data: quarterOptions } = await useAsyncData(
  'okr-quarters',
  () => okrApi.fetchQuarters(),
  {
    server: false,
    default: () => [],
  },
)

const search = ref('')
const status = ref('all')
const team = ref('all')
const quarter = ref(typeof route.query.quarter === 'string' ? route.query.quarter : 'all')

watchEffect(() => {
  if (quarter.value === 'all' && quarterOptions.value.length && !route.query.quarter) {
    quarter.value = quarterOptions.value.find((item) => item.isActive)?.name || 'all'
  }
})

const { data: okrsData, pending } = await useAsyncData(
  () => `okr-list-${quarter.value}`,
  () => okrApi.fetchOkrs({ quarter: quarter.value === 'all' ? undefined : quarter.value }),
  {
    server: false,
    default: () => [],
    watch: [quarter],
  },
)

const effectiveOkrs = computed(() => okrsData.value)
const effectiveQuarters = computed(() => quarterOptions.value.map((item) => item.name))
const teamOptions = computed(() => [...new Set(effectiveOkrs.value.map((item) => item.team))])

const filteredOkrs = computed(() =>
  effectiveOkrs.value.filter((okr) => {
    const matchesSearch =
      !search.value ||
      [okr.title, okr.owner, okr.team, okr.id].join(' ').toLowerCase().includes(search.value.toLowerCase())
    const matchesStatus = status.value === 'all' || okr.status === status.value
    const matchesTeam = team.value === 'all' || okr.team === team.value
    const matchesQuarter = quarter.value === 'all' || okr.quarter === quarter.value
    return matchesSearch && matchesStatus && matchesTeam && matchesQuarter
  }),
)
</script>

<template>
  <div class="space-y-6">
    <UiSectionCard title="Все OKR" subtitle="Регулярный рабочий экран с фильтрами, поиском и сортировкой.">
      <template #action>
        <NuxtLink to="/okrs/new" class="btn btn-primary">
          <Plus class="h-4 w-4" />
          Создать OKR
        </NuxtLink>
      </template>

      <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <input v-model="search" type="text" placeholder="Поиск по названию..." class="input-base">
        <select v-model="status" class="input-base">
          <option value="all">Все статусы</option>
          <option value="draft">{{ getOkrStatusLabel('draft') }}</option>
          <option value="on track">{{ getOkrStatusLabel('on track') }}</option>
          <option value="at risk">{{ getOkrStatusLabel('at risk') }}</option>
          <option value="completed">{{ getOkrStatusLabel('completed') }}</option>
        </select>
        <select v-model="team" class="input-base">
          <option value="all">Все команды</option>
          <option v-for="item in teamOptions" :key="item" :value="item">{{ item }}</option>
        </select>
        <select v-model="quarter" class="input-base">
          <option value="all">Все кварталы</option>
          <option v-for="item in effectiveQuarters" :key="item" :value="item">{{ item }}</option>
        </select>
      </div>

      <div v-if="search || status !== 'all' || team !== 'all' || quarter !== 'all'" class="mt-3 flex items-center gap-2 border-t border-ink-200 pt-3 text-sm">
        <span class="text-ink-500">Найдено:</span>
        <span class="font-medium text-ink-900">{{ filteredOkrs.length }} OKR</span>
        <button
          class="btn btn-ghost btn-sm ml-auto"
          @click="search = ''; status = 'all'; team = 'all'; quarter = 'all'"
        >
          <RotateCcw class="h-4 w-4" />
          Сбросить фильтры
        </button>
      </div>

      <div class="mt-6">
        <div v-if="!isHydrated || pending" class="block-radius border border-ink-200 bg-white px-4 py-6 text-sm text-ink-500">
          Загружаем список OKR...
        </div>
        <UiEmptyState
          v-else-if="!filteredOkrs.length"
          title="Список OKR пуст"
          description="Измени фильтры или создай цели в backend."
        />
        <OkrTable v-else :items="filteredOkrs" />
      </div>
    </UiSectionCard>
  </div>
</template>
