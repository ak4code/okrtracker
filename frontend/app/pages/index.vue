<script setup lang="ts">
definePageMeta({
  title: 'Дашборд',
})

import { Pencil } from 'lucide-vue-next'
import { Plus } from 'lucide-vue-next'
import type { KeyResultItem, OkrItem } from '~/composables/useOkrApi'
import {
  getKeyResultScaleBadgeClass,
  isKeyResultCompleted,
} from '~/composables/useKeyResultDisplay'
import { okrStatusOptions, okrStatusToApiMap } from '~/composables/useOkrForm'
import { formatOkrProgressScaleValue } from '~/composables/useProgressDisplay'

const okrApi = useOkrApi()
const selectedQuarter = useState<string>('dashboard-quarter', () => '')
const staleDays = 7
const isKeyResultEditModalOpen = ref(false)
const isCheckInModalOpen = ref(false)
const selectedKeyResult = ref<KeyResultItem | null>(null)
const editingStatusKeyResultId = ref<string | null>(null)
const updatingStatusKeyResultId = ref<string | null>(null)
const editingOkrStatusId = ref<string | null>(null)
const updatingOkrStatusId = ref<string | null>(null)
const statusDraft = ref<'draft' | 'on_track' | 'at_risk' | 'completed'>('draft')
const statusOptions = okrStatusOptions as { value: 'draft' | 'on_track' | 'at_risk' | 'completed', label: string }[]
const { data: quarters } = await useAsyncData(
  'okr-quarters',
  () => okrApi.fetchQuarters(),
  {
    server: false,
    default: () => [],
  },
)

watchEffect(() => {
  if (!selectedQuarter.value && quarters.value.length) {
    selectedQuarter.value = quarters.value.find((item) => item.isActive)?.name || quarters.value[0].name
  }
})

const { data: quarterOkrsData, pending } = await useAsyncData(
  () => `dashboard-okrs-${selectedQuarter.value || 'none'}`,
  () => okrApi.fetchOkrs({ quarter: selectedQuarter.value || undefined }),
  {
    server: false,
    default: () => [],
    watch: [selectedQuarter],
  },
)

const { data: quarterOkrDetailsData, pending: detailsPending } = await useAsyncData(
  () => `dashboard-okr-details-${selectedQuarter.value || 'none'}`,
  async () => {
    const okrs = await okrApi.fetchOkrs({ quarter: selectedQuarter.value || undefined })
    return Promise.all(okrs.map((item) => okrApi.fetchOkr(item.id)))
  },
  {
    server: false,
    default: () => [],
    watch: [selectedQuarter],
  },
)

const quarterOkrs = computed(() => quarterOkrsData.value)
const effectiveQuarterOkrs = computed(() => quarterOkrs.value)
const detailedQuarterOkrs = computed(() => quarterOkrDetailsData.value)
const teamNames = computed(() => [...new Set(effectiveQuarterOkrs.value.map((item) => item.team))])
const isStaleOkr = (updatedAtRaw: string) => {
  const updatedAtDate = new Date(updatedAtRaw)
  const staleThreshold = new Date()
  staleThreshold.setDate(staleThreshold.getDate() - staleDays)
  return updatedAtDate < staleThreshold
}

const quarterTeams = computed(() =>
  teamNames.value.map((teamName) => {
    const items = effectiveQuarterOkrs.value.filter((okr) => okr.team === teamName)
    const progress = items.length
      ? Math.round((items.reduce((sum, okr) => sum + okr.progress, 0) / items.length) * 10) / 10
      : 0

    return {
      name: teamName,
      progress,
      atRisk: items.filter((okr) => okr.status === 'at risk').length,
      overdue: items.filter((okr) => isStaleOkr(okr.updatedAtRaw)).length,
    }
  }),
)

const riskOkrs = computed(() =>
  effectiveQuarterOkrs.value.filter((item) => item.status === 'at risk').slice(0, 3),
)

const totalKeyResults = computed(() =>
  effectiveQuarterOkrs.value.reduce((sum, okr) => sum + okr.keyResultsCount, 0),
)

const completedKeyResults = computed(() =>
  effectiveQuarterOkrs.value.reduce((sum, okr) => sum + okr.completedKeyResultsCount, 0),
)

const recentOkrs = computed(() =>
  [...effectiveQuarterOkrs.value].sort((left, right) => right.updatedAtRaw.localeCompare(left.updatedAtRaw)).slice(0, 4),
)

const quarterStats = computed(() => [
  { label: 'Командные OKR', value: String(effectiveQuarterOkrs.value.length), hint: `Все команды · ${selectedQuarter.value}`, tone: 'sky' },
  { label: 'Закрытые KR', value: String(completedKeyResults.value), hint: `Статус completed · ${selectedQuarter.value}`, tone: 'mint' },
  { label: 'Команды в работе', value: String(teamNames.value.length), hint: `Активные команды · ${selectedQuarter.value}`, tone: 'ink' },
  { label: 'Проблемные OKR', value: String(riskOkrs.value.length), hint: `Статус at risk · ${selectedQuarter.value}`, tone: 'rose' },
])

const openKeyResultEditModal = (keyResult: KeyResultItem) => {
  selectedKeyResult.value = keyResult
  isKeyResultEditModalOpen.value = true
}

const openCheckInModal = (keyResult: KeyResultItem) => {
  if (isKeyResultCompleted(keyResult)) {
    return
  }

  selectedKeyResult.value = keyResult
  isCheckInModalOpen.value = true
}

const startKeyResultStatusEdit = (keyResult: KeyResultItem) => {
  editingStatusKeyResultId.value = keyResult.id
  statusDraft.value = okrStatusToApiMap[keyResult.status]
}

const stopKeyResultStatusEdit = () => {
  editingStatusKeyResultId.value = null
}

const startOkrStatusEdit = (okr: OkrItem) => {
  editingOkrStatusId.value = okr.id
  statusDraft.value = okrStatusToApiMap[okr.status]
}

const stopOkrStatusEdit = () => {
  editingOkrStatusId.value = null
}

const updateKeyResultStatus = async (keyResult: KeyResultItem) => {
  updatingStatusKeyResultId.value = keyResult.id

  try {
    const updatedOkr = await okrApi.updateKeyResult(keyResult.id, {
      title: keyResult.title,
      description: keyResult.description,
      value: String(keyResult.value),
      metric_type: keyResult.metricType,
      start_value: String(keyResult.start),
      current_value: String(keyResult.current),
      target_value: String(keyResult.target),
      status: statusDraft.value,
    })

    handleKeyResultSaved(updatedOkr)
    stopKeyResultStatusEdit()
  }
  finally {
    updatingStatusKeyResultId.value = null
  }
}

const updateOkrStatus = async (okr: OkrItem) => {
  updatingOkrStatusId.value = okr.id

  try {
    const updatedOkr = await okrApi.updateOkr(okr.id, {
      title: okr.title,
      description: okr.description,
      owner_id: okr.ownerId,
      team_id: okr.teamId,
      period_id: okr.periodId,
      status: statusDraft.value,
    })

    handleKeyResultSaved(updatedOkr)
    stopOkrStatusEdit()
  }
  finally {
    updatingOkrStatusId.value = null
  }
}

const handleKeyResultSaved = (updatedOkr: OkrItem) => {
  quarterOkrDetailsData.value = quarterOkrDetailsData.value.map((item) => (item.id === updatedOkr.id ? updatedOkr : item))
  quarterOkrsData.value = quarterOkrsData.value.map((item) => (
    item.id === updatedOkr.id
      ? {
          ...item,
          title: updatedOkr.title,
          description: updatedOkr.description,
          owner: updatedOkr.owner,
          team: updatedOkr.team,
          quarter: updatedOkr.quarter,
          status: updatedOkr.status,
          progress: updatedOkr.progress,
          keyResultsCount: updatedOkr.keyResultsCount,
          completedKeyResultsCount: updatedOkr.completedKeyResultsCount,
          comments: updatedOkr.comments,
          commentsList: updatedOkr.commentsList,
          changeLogs: updatedOkr.changeLogs,
          updatedAt: updatedOkr.updatedAt,
          updatedAtRaw: updatedOkr.updatedAtRaw,
        }
      : item
  ))
}
</script>

<template>
  <div class="min-w-0 w-full space-y-6">
    <section class="grid min-w-0 grid-auto-fit gap-4">
      <UiStatCard
        v-for="item in quarterStats"
        :key="item.label"
        :label="item.label"
        :value="item.value"
        :hint="item.hint"
        :tone="item.tone"
      />
    </section>

    <section class="grid min-w-0 gap-6">
      <UiSectionCard :title="`OKR команд · ${selectedQuarter}`" subtitle="Все командные OKR выбранного квартала для быстрого обзора.">
        <div v-if="pending || detailsPending" class="block-radius border border-ink-200 bg-white px-4 py-6 text-sm text-ink-500">
          Загружаем OKR...
        </div>
        <UiEmptyState
          v-else-if="!quarters.length"
          title="Кварталы ещё не созданы"
          description="Добавьте первый квартал в настройках системы."
        />
        <UiEmptyState
          v-else-if="!effectiveQuarterOkrs.length"
          title="Нет OKR в выбранном квартале"
          description="Создайте OKR в backend или выберите другой квартал."
        />
        <div v-else class="block-radius overflow-hidden border border-ink-200 bg-white">
          <div
            v-for="okr in detailedQuarterOkrs"
            :key="okr.id"
            class="border-b border-ink-200 last:border-b-0"
          >
            <NuxtLink
              :to="`/okrs/${okr.id}`"
              class="flex flex-wrap items-center justify-between gap-3 bg-ink-50 px-4 py-4 transition-colors hover:bg-ink-100/80"
            >
              <div class="min-w-0">
                <p class="text-xs uppercase tracking-[0.16em] text-ink-400">Objective [{{ okr.team }}]</p>
                <p class="mt-1 truncate text-sm font-semibold text-ink-900">{{ okr.title }}</p>
              </div>
              <div class="flex items-center gap-3">
                <select
                  v-if="editingOkrStatusId === okr.id"
                  v-model="statusDraft"
                  class="input-base min-w-36"
                  :disabled="updatingOkrStatusId === okr.id"
                  @click.stop
                  @change="updateOkrStatus(okr)"
                  @blur="stopOkrStatusEdit"
                >
                  <option v-for="item in statusOptions" :key="item.value" :value="item.value">
                    {{ item.label }}
                  </option>
                </select>
                <button
                  v-else
                  class="cursor-pointer"
                  :disabled="updatingOkrStatusId === okr.id"
                  @click.stop.prevent="startOkrStatusEdit(okr)"
                >
                  <UiStatusBadge :status="okr.status" size="sm" />
                </button>
                <span class="text-sm font-medium text-ink-500">{{ formatOkrProgressScaleValue(okr.progress) }}</span>
              </div>
            </NuxtLink>

            <div class="overflow-x-auto">
              <table class="min-w-full">
                <thead class="bg-white text-left text-xs uppercase tracking-[0.18em] text-ink-400">
                  <tr>
                    <th class="px-4 py-3 font-medium">Key Result</th>
                    <th class="px-4 py-3 font-medium">Значение KR</th>
                    <th class="px-4 py-3 font-medium">Текущее значение</th>
                    <th class="px-4 py-3 font-medium">Целевое значение</th>
                    <th class="px-4 py-3 font-medium">Статус</th>
                    <th class="px-4 py-3 font-medium">Прогресс KR</th>
                    <th class="px-4 py-3 font-medium">Последний check-in</th>
                    <th class="px-4 py-3 font-medium">Действия</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-ink-100 text-sm text-ink-600">
                  <tr
                    v-for="keyResult in okr.keyResults"
                    :key="keyResult.id"
                    class="transition-colors hover:bg-ink-50/60"
                  >
                    <td class="px-4 py-4">
                      <p class="max-w-[320px] truncate font-medium text-ink-900">{{ keyResult.title }}</p>
                    </td>
                    <td class="px-4 py-4">
                      <span
                        :class="[
                          getKeyResultScaleBadgeClass(keyResult.value),
                          'inline-flex min-w-14 items-center justify-center rounded-full border px-2.5 py-1 text-xs font-semibold',
                        ]"
                      >
                        {{ keyResult.value }}
                      </span>
                    </td>
                    <td class="px-4 py-4">{{ keyResult.current }} {{ keyResult.unit }}</td>
                    <td class="px-4 py-4">{{ keyResult.target }} {{ keyResult.unit }}</td>
                    <td class="px-4 py-4">
                      <select
                        v-if="editingStatusKeyResultId === keyResult.id"
                        v-model="statusDraft"
                        class="input-base min-w-36"
                        :disabled="updatingStatusKeyResultId === keyResult.id"
                        @change="updateKeyResultStatus(keyResult)"
                        @blur="stopKeyResultStatusEdit"
                      >
                        <option v-for="item in statusOptions" :key="item.value" :value="item.value">
                          {{ item.label }}
                        </option>
                      </select>
                      <button
                        v-else
                        class="cursor-pointer"
                        :disabled="updatingStatusKeyResultId === keyResult.id"
                        @click="startKeyResultStatusEdit(keyResult)"
                      >
                        <UiStatusBadge :status="keyResult.status" size="sm" />
                      </button>
                    </td>
                    <td class="px-4 py-4">
                      <div class="min-w-32 space-y-2">
                        <div class="text-xs text-ink-500">{{ Math.round(keyResult.progress * 100) }}%</div>
                        <UiProgressBar :value="keyResult.progress" :scale-value="keyResult.value" :show-value="false" compact />
                      </div>
                    </td>
                    <td class="px-4 py-4 text-xs text-ink-500">{{ keyResult.lastCheckIn }}</td>
                    <td class="px-4 py-4">
                      <div class="flex items-center gap-2">
                        <button
                          class="btn btn-secondary btn-icon h-8 min-h-8 w-8 min-w-8 rounded-[var(--radius-control)] p-0 disabled:cursor-not-allowed disabled:opacity-50"
                          aria-label="Создать check-in"
                          title="Создать check-in"
                          :disabled="isKeyResultCompleted(keyResult)"
                          @click.stop="openCheckInModal(keyResult)"
                        >
                          <Plus class="h-4 w-4" />
                        </button>
                        <button
                          class="btn btn-secondary btn-icon h-8 min-h-8 w-8 min-w-8 rounded-[var(--radius-control)] p-0"
                          aria-label="Редактировать KR"
                          title="Редактировать KR"
                          @click.stop="openKeyResultEditModal(keyResult)"
                        >
                          <Pencil class="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </UiSectionCard>
    </section>

    <section class="grid min-w-0 gap-6 xl:grid-cols-2">
      <UiSectionCard title="Требуют внимания" subtitle="OKR со статусом «Есть риск».">
        <UiEmptyState
          v-if="!riskOkrs.length"
          title="Проблемных OKR нет"
          description="В выбранном квартале нет целей со статусом «Есть риск»."
        />
        <div v-else class="grid gap-4">
          <NuxtLink
            v-for="okr in riskOkrs"
            :key="okr.id"
            :to="`/okrs/${okr.id}`"
            class="block block-radius border border-amber-200 bg-amber-100/60 p-4 transition-colors hover:bg-amber-100"
          >
            <div class="mb-2 flex items-start justify-between gap-3">
              <div>
                <p class="text-sm font-medium text-ink-900">{{ okr.title }}</p>
                <p class="mt-1 text-xs text-ink-500">{{ okr.owner }} · {{ okr.team }}</p>
              </div>
              <UiStatusBadge :status="okr.status" size="sm" />
            </div>
            <UiProgressBar :value="okr.progress" :scale-value="okr.progress" compact />
          </NuxtLink>
        </div>
      </UiSectionCard>

      <UiSectionCard title="Последние обновления" subtitle="Последние изменённые OKR выбранного квартала.">
        <UiEmptyState
          v-if="!recentOkrs.length"
          title="Обновлений пока нет"
          description="После появления OKR здесь будут последние изменения."
        />
        <div v-else class="space-y-3">
          <div
            v-for="item in recentOkrs"
            :key="item.id"
            class="block-radius border border-ink-200 p-4"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="font-medium text-ink-900">{{ item.title }}</p>
                <p class="mt-1 text-sm text-ink-500">{{ item.owner }} · {{ item.updatedAt }}</p>
              </div>
              <UiStatusBadge :status="item.status" size="sm" />
            </div>
          </div>
        </div>
      </UiSectionCard>
    </section>

    <UiSectionCard :title="`Квартальный обзор · ${selectedQuarter}`" subtitle="Сводка по командам и закрытым KR.">
      <div v-if="effectiveQuarterOkrs.length" class="grid min-w-0 gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <div class="surface-muted p-4">
          <p class="text-sm text-ink-500">Закрыто ключевых результатов</p>
          <p class="mt-2 text-4xl font-semibold text-ink-900">{{ completedKeyResults }}/{{ totalKeyResults }}</p>
          <p class="mt-2 text-sm text-ink-500">По всем OKR выбранного квартала</p>
        </div>
        <div class="grid min-w-0 gap-4 sm:grid-cols-2">
          <div v-for="team in quarterTeams" :key="team.name" class="block-radius border border-ink-200 p-4">
            <div class="flex items-center justify-between gap-3">
              <p class="font-medium text-ink-900">{{ team.name }}</p>
              <p class="text-sm text-ink-400">{{ formatOkrProgressScaleValue(team.progress) }}</p>
            </div>
            <div class="mt-3">
              <UiProgressBar :value="team.progress" :scale-value="team.progress" compact />
            </div>
            <div class="mt-2 text-xs text-ink-500">Есть риск: {{ team.atRisk }} · Без обновления {{ staleDays }}+ дн.: {{ team.overdue }}</div>
          </div>
        </div>
      </div>
      <UiEmptyState
        v-else
        title="Нет квартальной сводки"
        description="Создайте OKR в выбранном квартале, чтобы увидеть агрегированные показатели."
      />
    </UiSectionCard>

    <KeyResultEditModal
      v-if="selectedKeyResult"
      v-model="isKeyResultEditModalOpen"
      :key-result="selectedKeyResult"
      @saved="handleKeyResultSaved"
    />
    <CheckInCreateModal
      v-if="selectedKeyResult"
      v-model="isCheckInModalOpen"
      :key-result="selectedKeyResult"
      @saved="handleKeyResultSaved"
    />
  </div>
</template>
