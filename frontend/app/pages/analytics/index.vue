<script setup lang="ts">
definePageMeta({
  title: 'Аналитика',
})

import { AlertTriangle, Clock3, Target, TrendingUp } from 'lucide-vue-next'
import { formatOkrProgressScaleValue } from '~/composables/useProgressDisplay'

const okrApi = useOkrApi()
const selectedQuarter = ref('')
const staleDays = 7

const { data: quarterOptions } = await useAsyncData(
  'analytics-quarters',
  () => okrApi.fetchQuarters(),
  {
    server: false,
    default: () => [],
  },
)

watchEffect(() => {
  if (!selectedQuarter.value && quarterOptions.value.length) {
    selectedQuarter.value = quarterOptions.value.find((item) => item.isActive)?.name || quarterOptions.value[0].name
  }
})

const { data: okrsData, pending } = await useAsyncData(
  () => `analytics-okrs-${selectedQuarter.value || 'none'}`,
  () => okrApi.fetchOkrs({ quarter: selectedQuarter.value || undefined }),
  {
    server: false,
    default: () => [],
    watch: [selectedQuarter],
  },
)

const okrs = computed(() => okrsData.value)
const teams = computed(() => [...new Set(okrs.value.map((item) => item.team))])

const isStaleOkr = (updatedAtRaw: string) => {
  const updatedAtDate = new Date(updatedAtRaw)
  const staleThreshold = new Date()
  staleThreshold.setDate(staleThreshold.getDate() - staleDays)
  return updatedAtDate < staleThreshold
}

const analyticsStats = computed(() => [
  {
    label: 'OKR в квартале',
    value: String(okrs.value.length),
    hint: selectedQuarter.value || 'Квартал не выбран',
    icon: Target,
  },
  {
    label: 'Средний прогресс',
    value: okrs.value.length
      ? formatOkrProgressScaleValue(okrs.value.reduce((sum, item) => sum + item.progress, 0) / okrs.value.length)
      : '0',
    hint: 'По всем целям квартала',
    icon: TrendingUp,
  },
  {
    label: 'Есть риск',
    value: String(okrs.value.filter((item) => item.status === 'at risk').length),
    hint: 'Цели со статусом «Есть риск»',
    icon: AlertTriangle,
  },
  {
    label: 'Без обновления',
    value: String(okrs.value.filter((item) => isStaleOkr(item.updatedAtRaw)).length),
    hint: `${staleDays}+ дней без обновления`,
    icon: Clock3,
  },
])

const teamAnalytics = computed(() =>
  teams.value.map((teamName) => {
    const teamOkrs = okrs.value.filter((item) => item.team === teamName)
    const progress = teamOkrs.length
      ? teamOkrs.reduce((sum, item) => sum + item.progress, 0) / teamOkrs.length
      : 0

    return {
      name: teamName,
      okrsCount: teamOkrs.length,
      progress,
      atRiskCount: teamOkrs.filter((item) => item.status === 'at risk').length,
      completedKrCount: teamOkrs.reduce((sum, item) => sum + item.completedKeyResultsCount, 0),
      staleCount: teamOkrs.filter((item) => isStaleOkr(item.updatedAtRaw)).length,
    }
  }).sort((left, right) => right.atRiskCount - left.atRiskCount || right.staleCount - left.staleCount || left.name.localeCompare(right.name)),
)

const riskOkrs = computed(() =>
  okrs.value
    .filter((item) => item.status === 'at risk')
    .sort((left, right) => right.updatedAtRaw.localeCompare(left.updatedAtRaw)),
)

const staleOkrs = computed(() =>
  okrs.value
    .filter((item) => isStaleOkr(item.updatedAtRaw))
    .sort((left, right) => left.updatedAtRaw.localeCompare(right.updatedAtRaw)),
)
</script>

<template>
  <div class="space-y-6">
    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <article
        v-for="item in analyticsStats"
        :key="item.label"
        class="block-radius border border-ink-200 bg-white p-5"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-xs uppercase tracking-[0.18em] text-ink-400">{{ item.label }}</p>
            <p class="mt-3 text-3xl font-semibold text-ink-900">{{ item.value }}</p>
            <p class="mt-2 text-sm text-ink-500">{{ item.hint }}</p>
          </div>
          <div class="rounded-xl bg-ink-50 p-2 text-ink-500">
            <component :is="item.icon" class="h-4 w-4" />
          </div>
        </div>
      </article>
    </section>

    <section class="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
      <UiSectionCard title="Агрегат по командам" subtitle="Средний прогресс, риски и закрытые KR по командам выбранного квартала.">
        <div v-if="pending" class="block-radius border border-ink-200 bg-white px-4 py-6 text-sm text-ink-500">
          Загружаем аналитику...
        </div>

        <UiEmptyState
          v-else-if="!okrs.length"
          title="Нет данных для аналитики"
          description="Создайте OKR в выбранном квартале, чтобы увидеть агрегаты по командам."
        />

        <div v-else class="space-y-4">
          <div v-for="team in teamAnalytics" :key="team.name" class="block-radius border border-ink-200 p-5">
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="font-medium text-ink-900">{{ team.name }}</p>
                <p class="mt-1 text-sm text-ink-500">{{ team.okrsCount }} OKR · {{ team.completedKrCount }} закрытых KR</p>
              </div>
              <p class="font-display text-3xl font-semibold text-ink-900">{{ formatOkrProgressScaleValue(team.progress) }}</p>
            </div>
            <div class="mt-4">
              <UiProgressBar :value="team.progress" :scale-value="team.progress" compact />
            </div>
            <div class="mt-3 flex flex-wrap gap-2 text-xs text-ink-500">
              <span class="rounded-full bg-amber-100 px-3 py-1 text-amber-600">Есть риск: {{ team.atRiskCount }}</span>
              <span class="rounded-full bg-ink-100 px-3 py-1">Без обновления: {{ team.staleCount }}</span>
            </div>
          </div>
        </div>
      </UiSectionCard>

      <UiSectionCard title="Шкала прогресса" subtitle="Как читаются значения общего прогресса OKR.">
        <div class="space-y-3">
          <div class="block-radius bg-ink-100 p-4">
            <p class="font-medium text-ink-900">0</p>
            <p class="mt-1 text-sm text-ink-500">Ни один KR ещё не закрыт</p>
          </div>
          <div class="block-radius bg-sky-100 p-4">
            <p class="font-medium text-ink-900">0.3</p>
            <p class="mt-1 text-sm text-ink-500">Закрыт первый KR</p>
          </div>
          <div class="block-radius bg-amber-100 p-4">
            <p class="font-medium text-ink-900">0.7</p>
            <p class="mt-1 text-sm text-ink-500">Закрыт KR со значением 0.7</p>
          </div>
          <div class="block-radius bg-mint-100 p-4">
            <p class="font-medium text-ink-900">1.0</p>
            <p class="mt-1 text-sm text-ink-500">Закрыт максимальный KR, цель достигнута</p>
          </div>
        </div>
      </UiSectionCard>
    </section>

    <section class="grid gap-6 xl:grid-cols-2">
      <UiSectionCard title="Проблемные OKR" subtitle="Цели со статусом «Есть риск» в выбранном квартале.">
        <UiEmptyState
          v-if="!riskOkrs.length"
          title="Проблемных OKR нет"
          description="В выбранном квартале нет целей со статусом «Есть риск»."
        />

        <div v-else class="space-y-3">
          <NuxtLink
            v-for="okr in riskOkrs"
            :key="okr.id"
            :to="`/okrs/${okr.id}`"
            class="block block-radius border border-ink-200 p-4 transition-colors hover:bg-ink-50"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-medium text-ink-900">{{ okr.title }}</p>
                <p class="mt-1 text-sm text-ink-500">{{ okr.team }} · {{ okr.owner }}</p>
              </div>
              <UiStatusBadge :status="okr.status" />
            </div>
            <div class="mt-3">
              <UiProgressBar :value="okr.progress" :scale-value="okr.progress" compact />
            </div>
          </NuxtLink>
        </div>
      </UiSectionCard>

      <UiSectionCard :title="`Без обновления ${staleDays}+ дней`" subtitle="Цели, которые давно не обновлялись.">
        <UiEmptyState
          v-if="!staleOkrs.length"
          title="Просроченных обновлений нет"
          description="Все OKR обновлялись в рамках ожидаемого окна."
        />

        <div v-else class="space-y-3">
          <NuxtLink
            v-for="okr in staleOkrs"
            :key="okr.id"
            :to="`/okrs/${okr.id}`"
            class="block block-radius border border-ink-200 p-4 transition-colors hover:bg-ink-50"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-medium text-ink-900">{{ okr.title }}</p>
                <p class="mt-1 text-sm text-ink-500">{{ okr.team }} · {{ okr.owner }}</p>
              </div>
              <p class="text-xs text-ink-400">{{ okr.updatedAt }}</p>
            </div>
            <div class="mt-3 flex items-center justify-between gap-3 text-sm text-ink-500">
              <span>{{ okr.completedKeyResultsCount }}/{{ okr.keyResultsCount }} закрытых KR</span>
              <span>{{ formatOkrProgressScaleValue(okr.progress) }}</span>
            </div>
          </NuxtLink>
        </div>
      </UiSectionCard>
    </section>
  </div>
</template>
