<script setup lang="ts">
definePageMeta({
  title: 'Детали OKR',
})

import { ArrowLeft, Clock3, Flag, MessageSquareText, Pencil, Plus, Target, TrendingUp } from 'lucide-vue-next'
import CommentCreateModal from '~/components/CommentCreateModal.vue'
import type { CheckInItem, KeyResultItem, OkrItem } from '~/composables/useOkrApi'
import {
  formatKeyResultValue,
  formatMetricValue,
  formatPercentProgress,
  getCommentInitials,
  getKeyResultScaleBadgeClass,
  getKeyResultScaleClass,
  isKeyResultCompleted,
} from '~/composables/useKeyResultDisplay'
import { formatOkrProgressScaleValue } from '~/composables/useProgressDisplay'

const route = useRoute()
const okrApi = useOkrApi()
const isEditModalOpen = ref(false)
const isKeyResultCreateModalOpen = ref(false)
const isKeyResultModalOpen = ref(false)
const isCheckInModalOpen = ref(false)
const isCheckInEditModalOpen = ref(false)
const isDeleteCheckInConfirmOpen = ref(false)
const isCommentCreateModalOpen = ref(false)
const selectedKeyResult = ref<KeyResultItem | null>(null)
const selectedCheckIn = ref<CheckInItem | null>(null)
const isDeletingCheckIn = ref(false)
const visibleChangeLogsCount = ref(3)
const isHydrated = ref(false)

onMounted(() => {
  isHydrated.value = true
})

const { data: okr, pending } = await useAsyncData(
  () => `okr-detail-${route.params.id}`,
  () => okrApi.fetchOkr(String(route.params.id)),
  {
    server: false,
    default: () => null,
    watch: [() => route.params.id],
  },
)

const effectiveOkr = computed(() => okr.value)
const visibleChangeLogs = computed(() => effectiveOkr.value?.changeLogs.slice(0, visibleChangeLogsCount.value) || [])
const hasMoreChangeLogs = computed(() => (effectiveOkr.value?.changeLogs.length || 0) > visibleChangeLogsCount.value)

watch(
  () => effectiveOkr.value?.id,
  () => {
    visibleChangeLogsCount.value = 3
  },
)

const fullHistory = computed(() =>
  (effectiveOkr.value?.keyResults.flatMap((item) =>
    item.history.map((historyItem) => ({
      ...historyItem,
      keyResultId: item.id,
      keyResultTitle: item.title,
      metricType: item.metricType,
      unit: item.unit,
    })),
  ) || [])
    .sort((left, right) => right.dateRaw.localeCompare(left.dateRaw)),
)

const atRiskKeyResults = computed(() =>
  effectiveOkr.value?.keyResults.filter((item) => item.status === 'at risk').length || 0,
)

const doneKeyResults = computed(() =>
  effectiveOkr.value?.keyResults.filter((item) => item.status === 'completed').length || 0,
)

const detailStats = computed(() => {
  if (!effectiveOkr.value) {
    return []
  }

  return [
    {
      label: 'Прогресс цели',
      value: formatOkrProgressScaleValue(effectiveOkr.value.progress),
      hint: 'Сводный прогресс по OKR',
      icon: TrendingUp,
    },
    {
      label: 'Key results',
      value: `${doneKeyResults.value}/${effectiveOkr.value.keyResultsCount}`,
      hint: 'Завершено ключевых результатов',
      icon: Target,
    },
    {
      label: 'Комментарии',
      value: String(effectiveOkr.value.comments),
      hint: 'Контекст и договоренности',
      icon: MessageSquareText,
    },
    {
      label: 'Есть риск',
      value: String(atRiskKeyResults.value),
      hint: 'KR со статусом at risk',
      icon: Flag,
    },
  ]
})

const handleOkrSaved = (updatedOkr: OkrItem) => {
  okr.value = updatedOkr
}

const openKeyResultModal = (keyResult: KeyResultItem) => {
  selectedKeyResult.value = keyResult
  isKeyResultModalOpen.value = true
}

const openCheckInModal = (keyResult: KeyResultItem) => {
  if (isKeyResultCompleted(keyResult)) {
    return
  }

  selectedKeyResult.value = keyResult
  isCheckInModalOpen.value = true
}

const openCheckInEditModal = (checkIn: CheckInItem) => {
  selectedCheckIn.value = checkIn
  isCheckInEditModalOpen.value = true
}

const deleteCheckIn = async (checkIn: CheckInItem) => {
  selectedCheckIn.value = checkIn
  isDeleteCheckInConfirmOpen.value = true
}

const confirmDeleteCheckIn = async () => {
  if (!selectedCheckIn.value) {
    return
  }

  isDeletingCheckIn.value = true

  try {
    const updatedOkr = await okrApi.deleteCheckIn(selectedCheckIn.value.id)
    handleOkrSaved(updatedOkr)
    isDeleteCheckInConfirmOpen.value = false
    selectedCheckIn.value = null
  }
  finally {
    isDeletingCheckIn.value = false
  }
}

const loadMoreChangeLogs = () => {
  visibleChangeLogsCount.value += 3
}
</script>

<template>
  <div class="space-y-6">
    <div v-if="!isHydrated || pending" class="block-radius border border-ink-200 bg-white px-4 py-6 text-sm text-ink-500">
      Загружаем карточку OKR...
    </div>

    <UiEmptyState
      v-else-if="!effectiveOkr"
      title="OKR не найден"
      description="Проверь идентификатор или создай цель в backend."
    />

    <div v-else class="space-y-6">
      <section class="block-radius overflow-hidden border border-ink-200 bg-linear-to-br from-[#f6fbff] via-white to-[#f4f8f1]">
        <div class="border-b border-ink-200/80 px-6 py-5 sm:px-8">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <NuxtLink
              to="/okrs"
              class="inline-flex items-center gap-2 text-sm font-medium text-ink-500 transition-colors hover:text-ink-900"
            >
              <ArrowLeft class="h-4 w-4" />
              Ко всем OKR
            </NuxtLink>

            <button
              class="btn btn-secondary"
              @click="isEditModalOpen = true"
            >
              <Pencil class="h-4 w-4" />
              Редактировать OKR
            </button>
          </div>
        </div>

        <div class="grid gap-8 px-6 py-8 sm:px-8 xl:grid-cols-[1.35fr_0.65fr]">
          <div class="space-y-6">
            <div class="flex flex-wrap items-start justify-between gap-4">
              <div class="max-w-3xl">
                <p class="text-xs uppercase tracking-[0.22em] text-ink-400">{{ effectiveOkr.quarter }} · {{ effectiveOkr.team }}</p>
                <h1 class="mt-3 text-3xl leading-tight font-semibold text-ink-900 sm:text-4xl">{{ effectiveOkr.title }}</h1>
                <p class="mt-4 max-w-2xl text-sm leading-6 text-ink-600">{{ effectiveOkr.description || 'Описание цели пока не заполнено.' }}</p>
              </div>

              <UiStatusBadge :status="effectiveOkr.status" />
            </div>

            <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <div v-for="item in detailStats" :key="item.label" class="block-radius border border-white/70 bg-white/90 p-4 shadow-sm backdrop-blur">
                <div class="flex items-start justify-between gap-4">
                  <div>
                    <p class="text-xs uppercase tracking-[0.18em] text-ink-400">{{ item.label }}</p>
                    <p class="mt-3 text-2xl font-semibold text-ink-900">{{ item.value }}</p>
                    <p class="mt-2 text-sm text-ink-500">{{ item.hint }}</p>
                  </div>
                  <div class="rounded-xl bg-ink-50 p-2 text-ink-500">
                    <component :is="item.icon" class="h-4 w-4" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="block-radius border border-ink-200 bg-white/90 p-6 shadow-sm">
            <div class="flex items-center justify-between gap-4">
              <div>
                <p class="text-xs uppercase tracking-[0.18em] text-ink-400">Сводка</p>
                <h2 class="mt-2 text-lg font-semibold text-ink-900">Текущее состояние цели</h2>
              </div>
              <Clock3 class="h-5 w-5 text-ink-400" />
            </div>

            <div class="mt-6">
              <div class="flex items-end justify-between gap-4">
                <div>
                  <p class="text-sm text-ink-500">Общий прогресс</p>
                  <p class="mt-2 text-4xl font-semibold text-ink-900">{{ formatOkrProgressScaleValue(effectiveOkr.progress) }}</p>
                </div>
                <p class="text-sm text-ink-500">Обновлено {{ effectiveOkr.updatedAt }}</p>
              </div>
              <div class="mt-4">
                <UiProgressBar :value="effectiveOkr.progress" :scale-value="effectiveOkr.progress" />
              </div>
            </div>

            <dl class="mt-6 space-y-4 text-sm">
              <div class="flex items-start justify-between gap-4 border-t border-ink-200 pt-4">
                <dt class="text-ink-500">Владелец</dt>
                <dd class="font-medium text-ink-900">{{ effectiveOkr.owner }}</dd>
              </div>
              <div class="flex items-start justify-between gap-4 border-t border-ink-200 pt-4">
                <dt class="text-ink-500">Команда</dt>
                <dd class="font-medium text-ink-900">{{ effectiveOkr.team }}</dd>
              </div>
              <div class="flex items-start justify-between gap-4 border-t border-ink-200 pt-4">
                <dt class="text-ink-500">Период</dt>
                <dd class="font-medium text-ink-900">{{ effectiveOkr.quarter }}</dd>
              </div>
              <div class="flex items-start justify-between gap-4 border-t border-ink-200 pt-4">
                <dt class="text-ink-500">Комментариев</dt>
                <dd class="font-medium text-ink-900">{{ effectiveOkr.comments }}</dd>
              </div>
            </dl>
          </div>
        </div>
      </section>

      <div class="space-y-6">
        <UiSectionCard title="Key results" subtitle="Ключевые результаты, которые формируют прогресс цели.">
          <template #action>
            <button class="btn btn-primary" @click="isKeyResultCreateModalOpen = true">
              <Plus class="h-4 w-4" />
              Добавить KR
            </button>
          </template>

          <UiEmptyState
            v-if="!effectiveOkr.keyResults.length"
            title="Key results пока нет"
            description="Добавьте ключевые результаты в backend, чтобы отслеживать прогресс цели."
          />

          <div v-else class="space-y-4">
            <article
              v-for="(kr, index) in effectiveOkr.keyResults"
              :key="kr.id"
              class="block-radius border p-5"
              :class="getKeyResultScaleClass(kr.value)"
            >
              <div class="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p class="text-xs uppercase tracking-[0.18em] text-ink-400">KR {{ index + 1 }}</p>
                  <h3 class="mt-2 text-base font-semibold text-ink-900">{{ kr.title }}</h3>
                  <p class="mt-2 text-sm text-ink-500">{{ kr.owner }} · Последний check-in: {{ kr.lastCheckIn }}</p>
                </div>
                <div class="flex items-center gap-3">
                  <p
                    class="rounded-full border px-3 py-1 text-sm font-medium"
                    :class="getKeyResultScaleBadgeClass(kr.value)"
                  >
                    {{ formatKeyResultValue(kr.value) }}
                  </p>
                  <UiStatusBadge :status="kr.status" size="sm" />
                </div>
              </div>

              <p v-if="kr.description" class="mt-4 text-sm leading-6 text-ink-600">
                {{ kr.description }}
              </p>

              <div class="mt-5 grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
                <div class="grid gap-3 sm:grid-cols-2">
                  <div class="rounded-xl border border-ink-200 bg-white px-4 py-3">
                    <p class="text-xs uppercase tracking-[0.16em] text-ink-400">Текущее значение</p>
                    <p class="mt-2 font-semibold text-ink-900">{{ formatMetricValue(kr.current, kr.unit) }}</p>
                  </div>
                  <div class="rounded-xl border border-ink-200 bg-white px-4 py-3">
                    <p class="text-xs uppercase tracking-[0.16em] text-ink-400">Целевое значение</p>
                    <p class="mt-2 font-semibold text-ink-900">{{ formatMetricValue(kr.target, kr.unit) }}</p>
                  </div>
                </div>

                <div class="rounded-xl border border-ink-200 bg-white px-4 py-3">
                  <div class="flex items-center justify-between gap-3">
                    <p class="text-xs uppercase tracking-[0.16em] text-ink-400">Прогресс KR</p>
                    <div class="flex items-center gap-3">
                      <p class="text-sm font-medium text-ink-500">{{ formatPercentProgress(kr.progress) }}</p>
                      <button
                        class="btn btn-primary btn-sm disabled:cursor-not-allowed disabled:opacity-50"
                        :disabled="isKeyResultCompleted(kr)"
                        @click="openCheckInModal(kr)"
                      >
                        Check-in
                      </button>
                      <button
                        class="btn btn-secondary btn-sm"
                        @click="openKeyResultModal(kr)"
                      >
                        <Pencil class="h-4 w-4" />
                        Редактировать
                      </button>
                    </div>
                  </div>
                  <div class="mt-3">
                    <UiProgressBar
                      :value="kr.progress"
                      :scale-value="kr.value"
                      :show-value="false"
                      compact
                    />
                  </div>
                </div>
              </div>

              <div v-if="kr.history.length" class="mt-5 block-radius border border-ink-200 bg-white p-4">
                <p class="text-xs uppercase tracking-[0.16em] text-ink-400">Последние обновления</p>
                <div class="mt-3 space-y-3">
                  <div
                    v-for="item in kr.history.slice(0, 2)"
                    :key="item.id"
                    class="flex items-start justify-between gap-3 border-t border-ink-100 pt-3 first:border-t-0 first:pt-0"
                  >
                    <div>
                      <p class="text-sm font-medium text-ink-900">{{ item.author }}</p>
                      <p class="mt-1 text-sm text-ink-500">{{ item.note || 'Без комментария' }}</p>
                    </div>
                    <div class="text-right">
                      <p class="text-sm font-medium text-ink-900">{{ item.value }}</p>
                      <p class="mt-1 text-xs text-ink-400">{{ item.date }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </article>
          </div>
        </UiSectionCard>

        <div class="space-y-6">
          <UiSectionCard title="Комментарии" subtitle="Контекст, договоренности и уточнения по цели.">
            <template #action>
              <button class="btn btn-primary" @click="isCommentCreateModalOpen = true">
                <MessageSquareText class="h-4 w-4" />
                Добавить комментарий
              </button>
            </template>

            <div class="space-y-4">
              <UiEmptyState
                v-if="!effectiveOkr.commentsList.length"
                title="Комментариев пока нет"
                description="Оставь первый комментарий, чтобы зафиксировать контекст по цели."
              />

              <div
                v-else
                class="block-radius border border-ink-200 bg-linear-to-b from-sky-50/70 via-white to-ink-50 p-4 sm:p-5"
              >
                <div class="space-y-4">
                <article
                  v-for="comment in effectiveOkr.commentsList"
                  :key="comment.id"
                  class="flex items-end gap-3"
                >
                  <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-sky-400 to-sky-500 text-xs font-semibold text-white shadow-sm">
                    {{ getCommentInitials(comment.author) }}
                  </div>
                  <div class="max-w-[min(92%,42rem)]">
                    <div class="rounded-[22px] rounded-bl-md border border-sky-200/70 bg-white px-4 py-3 shadow-sm">
                      <div class="flex items-start justify-between gap-4">
                        <p class="text-sm font-medium text-ink-900">{{ comment.author }}</p>
                        <p class="shrink-0 pt-0.5 text-[11px] text-ink-400">{{ comment.createdAt }}</p>
                      </div>
                      <p class="mt-2 text-sm leading-6 text-ink-700">{{ comment.text }}</p>
                    </div>
                  </div>
                </article>
                </div>
              </div>
            </div>
          </UiSectionCard>

          <UiSectionCard title="Check-in история" subtitle="Лента обновлений по всем ключевым результатам.">
            <UiEmptyState
              v-if="!fullHistory.length"
              title="Check-in пока нет"
              description="История обновлений появится после первых check-in."
            />

            <div v-else>
              <CheckinTimeline :history="fullHistory" @edit="openCheckInEditModal" @delete="deleteCheckIn" />
            </div>
          </UiSectionCard>

          <UiSectionCard title="История изменений" subtitle="Аудит действий по цели и связанным объектам.">
            <UiEmptyState
              v-if="!effectiveOkr.changeLogs.length"
              title="История изменений пока пуста"
              description="Записи аудита появятся после действий в backend."
            />

            <div v-else class="space-y-2.5">
              <div
                v-for="item in visibleChangeLogs"
                :key="item.id"
                class="block-radius border border-ink-200 bg-white px-3 py-3"
              >
                <div class="flex items-start justify-between gap-2">
                  <div class="min-w-0">
                    <div class="flex flex-wrap items-center gap-2">
                      <p class="text-sm font-medium text-ink-900">{{ item.action }}</p>
                      <span class="rounded-full border border-ink-200 bg-ink-50 px-2.5 py-1 text-[11px] font-medium tracking-[0.12em] text-ink-500 uppercase">
                        {{ item.entityLabel }}
                      </span>
                    </div>
                    <p v-if="item.entityName" class="mt-1.5 text-sm font-medium text-ink-700">{{ item.entityName }}</p>
                    <p class="mt-1 text-xs text-ink-500">{{ item.author }}</p>
                  </div>
                  <p class="shrink-0 text-[11px] text-ink-400">{{ item.createdAt }}</p>
                </div>

                <div v-if="item.details.length" class="mt-3 space-y-1.5 border-t border-ink-100 pt-2.5">
                  <p
                    v-for="detail in item.details"
                    :key="detail"
                    class="text-sm leading-5 text-ink-600"
                  >
                    {{ detail }}
                  </p>
                </div>
              </div>

              <button
                v-if="hasMoreChangeLogs"
                class="btn btn-secondary btn-sm w-full"
                @click="loadMoreChangeLogs"
              >
                Загрузить еще
              </button>
            </div>
          </UiSectionCard>

        </div>
      </div>

      <OkrEditModal
        v-model="isEditModalOpen"
        :okr="effectiveOkr"
        @saved="handleOkrSaved"
      />

      <KeyResultEditModal
        v-if="selectedKeyResult"
        v-model="isKeyResultModalOpen"
        :key-result="selectedKeyResult"
        @saved="handleOkrSaved"
      />

      <KeyResultCreateModal
        v-model="isKeyResultCreateModalOpen"
        :okr="effectiveOkr"
        @saved="handleOkrSaved"
      />

      <CheckInCreateModal
        v-if="selectedKeyResult"
        v-model="isCheckInModalOpen"
        :key-result="selectedKeyResult"
        @saved="handleOkrSaved"
      />

      <CheckInEditModal
        v-if="selectedCheckIn"
        v-model="isCheckInEditModalOpen"
        :check-in="selectedCheckIn"
        @saved="handleOkrSaved"
      />

      <CommentCreateModal
        v-model="isCommentCreateModalOpen"
        :okr="effectiveOkr"
        @saved="handleOkrSaved"
      />

      <ConfirmModal
        v-model="isDeleteCheckInConfirmOpen"
        title="Удалить check-in?"
        :description="selectedCheckIn ? `Запись по ${selectedCheckIn.keyResultTitle || 'key result'} будет удалена, а значение KR пересчитается.` : ''"
        confirm-label="Удалить"
        :is-loading="isDeletingCheckIn"
        @confirm="confirmDeleteCheckIn"
      />
    </div>
  </div>
</template>
