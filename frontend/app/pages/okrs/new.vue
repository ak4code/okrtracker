<script setup lang="ts">
import { ClipboardList, Layers3, Plus, Save, Target, UserRound } from 'lucide-vue-next'
import type { OkrCreatePayload } from '~/app/composables/useOkrApi'
import {
  normalizeFormValue,
} from '~/composables/useOkrForm'

definePageMeta({
  title: 'Создать OKR',
})

type FormStatus = OkrCreatePayload['status']
type MetricType = OkrCreatePayload['key_results'][number]['metric_type']

interface KeyResultForm {
  localId: number
  title: string
  description: string
  metricType: MetricType
  startValue: string | number
  currentValue: string | number
  targetValue: string | number
  status: FormStatus
}

const okrApi = useOkrApi()
const auth = useAuth()

const createEmptyKeyResult = (localId: number): KeyResultForm => ({
  localId,
  title: '',
  description: '',
  metricType: 'number',
  startValue: '0',
  currentValue: '0',
  targetValue: '',
  status: 'draft',
})

const form = ref({
  title: '',
  description: '',
  ownerId: '',
  teamId: '',
  periodId: '',
  status: 'draft' as FormStatus,
})

const fieldError = ref('')
const submitError = ref('')
const isSubmitting = ref(false)
const keyResultSeed = ref(2)
const keyResults = ref<KeyResultForm[]>([createEmptyKeyResult(1)])

const { users, teams, quarters, isLoading } = await useOkrLookups('okr-create')

watchEffect(() => {
  if (!form.value.ownerId && users.value.length) {
    const currentUserId = auth.currentUser.value?.id
    const matchedUser = currentUserId
      ? users.value.find((item) => item.id === currentUserId)
      : null

    form.value.ownerId = String(matchedUser?.id || users.value[0].id)
  }

  if (!form.value.teamId && teams.value.length) {
    form.value.teamId = String(teams.value[0].id)
  }

  if (!form.value.periodId && quarters.value.length) {
    form.value.periodId = String(quarters.value.find((item) => item.isActive)?.id || quarters.value[0].id)
  }
})

const isFormReady = computed(() => users.value.length && teams.value.length && quarters.value.length)
const selectedOwnerLabel = computed(() => {
  const selectedUser = users.value.find((item) => String(item.id) === form.value.ownerId)
  if (!selectedUser) {
    return 'Не выбран'
  }

  return selectedUser.firstName || selectedUser.lastName
    ? `${selectedUser.firstName} ${selectedUser.lastName}`.trim()
    : selectedUser.email
})

const selectedTeamLabel = computed(() => teams.value.find((item) => String(item.id) === form.value.teamId)?.name || 'Не выбрана')
const selectedQuarterLabel = computed(() => quarters.value.find((item) => String(item.id) === form.value.periodId)?.name || 'Не выбран')
const completedDraftCount = computed(() => keyResults.value.filter((item) => normalizeFormValue(item.targetValue)).length)

const addKeyResult = () => {
  keyResults.value.push(createEmptyKeyResult(keyResultSeed.value))
  keyResultSeed.value += 1
}

const removeKeyResult = (localId: number) => {
  if (keyResults.value.length === 1) {
    return
  }

  keyResults.value = keyResults.value.filter((item) => item.localId !== localId)
}

const validateForm = () => {
  if (!form.value.title.trim()) {
    return 'Название цели обязательно.'
  }

  if (!form.value.ownerId || !form.value.teamId || !form.value.periodId) {
    return 'Выбери владельца, команду и квартал.'
  }

  if (!keyResults.value.length) {
    return 'Добавь хотя бы один ключевой результат.'
  }

  for (const [index, keyResult] of keyResults.value.entries()) {
    if (!keyResult.title.trim()) {
      return `Заполни название для KR #${index + 1}.`
    }

    if (!normalizeFormValue(keyResult.targetValue)) {
      return `Заполни целевое значение для KR #${index + 1}.`
    }
  }

  return ''
}

const submitForm = async () => {
  fieldError.value = ''
  submitError.value = ''

  const validationError = validateForm()
  if (validationError) {
    fieldError.value = validationError
    return
  }

  isSubmitting.value = true

  try {
    const createdOkr = await okrApi.createOkr({
      title: form.value.title.trim(),
      description: form.value.description.trim(),
      owner_id: Number(form.value.ownerId),
      team_id: Number(form.value.teamId),
      period_id: Number(form.value.periodId),
      status: form.value.status,
      key_results: keyResults.value.map((item) => ({
        title: item.title.trim(),
        description: item.description.trim(),
        metric_type: item.metricType,
        start_value: normalizeFormValue(item.startValue) || '0',
        current_value: normalizeFormValue(item.currentValue) || normalizeFormValue(item.startValue) || '0',
        target_value: normalizeFormValue(item.targetValue),
        status: item.status,
      })),
    })

    await navigateTo(`/okrs/${createdOkr.id}`)
  }
  catch (error: any) {
    submitError.value =
      error?.data?.detail ||
      error?.data?.key_results?.[0] ||
      error?.data?.title?.[0] ||
      'Не удалось создать OKR.'
  }
  finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <section class="block-radius overflow-hidden border border-ink-200 bg-linear-to-br from-[#f7fbff] via-white to-[#f6faf4]">
      <div class="flex flex-col gap-4 px-5 py-5 sm:px-6 sm:py-5 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <div class="inline-flex items-center gap-2 rounded-full border border-white/80 bg-white/85 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-teal-700 shadow-sm">
            <UserRound class="h-3.5 w-3.5" />
            Новый OKR
          </div>
          <h1 class="mt-3 text-2xl font-semibold text-ink-900 sm:text-[1.75rem]">Создание OKR</h1>
          <p class="mt-2 max-w-3xl text-sm leading-6 text-ink-600">
            Опиши цель и добавь измеримые key results. Справа останется краткая сводка и сохранение.
          </p>
        </div>

        <div class="flex flex-wrap gap-2 text-xs font-medium text-ink-600 xl:max-w-[360px] xl:justify-end">
          <span class="rounded-full bg-white/90 px-3 py-1 shadow-sm">{{ keyResults.length }} KR</span>
          <span class="rounded-full bg-white/90 px-3 py-1 shadow-sm">{{ completedDraftCount }} с целевым значением</span>
          <span class="rounded-full bg-white/90 px-3 py-1 shadow-sm">{{ selectedQuarterLabel }}</span>
        </div>
      </div>
    </section>

    <div v-if="isLoading" class="block-radius border border-ink-200 bg-white px-4 py-6 text-sm text-ink-500">
      Загружаем справочники формы...
    </div>

    <UiEmptyState
      v-else-if="!isFormReady"
      title="Недостаточно данных для создания OKR"
      description="Сначала создай пользователей, команды и кварталы в настройках."
    />

    <div v-else class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
      <form class="space-y-6" @submit.prevent="submitForm">
        <section class="surface p-6">
          <div class="mb-5 flex items-start gap-3">
            <div class="rounded-2xl bg-emerald-100 p-2 text-emerald-600">
              <ClipboardList class="h-5 w-5" />
            </div>
            <div>
              <h2 class="text-lg font-semibold text-ink-900">Objective</h2>
              <p class="mt-1 text-sm text-ink-500">Базовая информация о цели, владельце и периоде.</p>
            </div>
          </div>

          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2 md:col-span-2">
              <label class="text-sm font-medium text-ink-600">Название цели</label>
              <input
                v-model="form.title"
                type="text"
                placeholder="Например: Повысить предсказуемость delivery"
                class="input-base"
              >
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium text-ink-600">Владелец</label>
              <select v-model="form.ownerId" class="input-base">
                <option v-for="item in users" :key="item.id" :value="String(item.id)">
                  {{ item.firstName || item.lastName ? `${item.firstName} ${item.lastName}`.trim() : item.email }}
                </option>
              </select>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium text-ink-600">Статус</label>
              <select v-model="form.status" class="input-base">
                <option v-for="item in statusOptions" :key="item.value" :value="item.value">
                  {{ item.label }}
                </option>
              </select>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium text-ink-600">Команда</label>
              <select v-model="form.teamId" class="input-base">
                <option v-for="item in teams" :key="item.id" :value="String(item.id)">
                  {{ item.name }}
                </option>
              </select>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium text-ink-600">Период</label>
              <select v-model="form.periodId" class="input-base">
                <option v-for="item in quarters" :key="item.id" :value="String(item.id)">
                  {{ item.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="mt-4 space-y-2">
            <label class="text-sm font-medium text-ink-600">Описание</label>
            <textarea
              v-model="form.description"
              rows="5"
              class="input-base resize-none"
              placeholder="Кратко опиши, что должно измениться и какой эффект ожидается."
            />
          </div>
        </section>

        <section class="surface p-6">
          <div class="mb-5 flex flex-wrap items-start justify-between gap-4">
            <div class="flex items-start gap-3">
              <div class="rounded-2xl bg-sky-100 p-2 text-sky-500">
                <Layers3 class="h-5 w-5" />
              </div>
              <div>
                <h2 class="text-lg font-semibold text-ink-900">Key Results</h2>
                <p class="mt-1 text-sm text-ink-500">Каждый KR должен быть измеримым и иметь целевое значение.</p>
              </div>
            </div>

            <button
              type="button"
              class="btn btn-secondary"
              @click="addKeyResult"
            >
              <Plus class="h-4 w-4" />
              Добавить KR
            </button>
          </div>

          <div class="space-y-4">
            <OkrCreateKeyResultCard
              v-for="(item, index) in keyResults"
              :key="item.localId"
              :item="item"
              :index="index"
              :can-remove="keyResults.length > 1"
              @remove="removeKeyResult"
            />
          </div>
        </section>
      </form>

      <aside class="space-y-4 xl:sticky xl:top-6 xl:self-start">
        <section class="surface overflow-hidden p-0">
          <div class="border-b border-ink-200 bg-ink-900 px-5 py-4 text-white">
            <p class="text-xs uppercase tracking-[0.18em] text-white/50">Сводка</p>
            <h2 class="mt-2 text-lg font-semibold">Что будет создано</h2>
          </div>

          <div class="space-y-4 p-5">
            <div class="flex items-start gap-3">
              <div class="rounded-xl bg-ink-100 p-2 text-ink-600">
                <Target class="h-4 w-4" />
              </div>
              <div>
                <p class="text-xs uppercase tracking-[0.16em] text-ink-400">Цель</p>
                <p class="mt-1 text-sm font-medium text-ink-900">{{ form.title.trim() || 'Название пока не заполнено' }}</p>
              </div>
            </div>

            <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
              <div class="block-radius border border-ink-200 bg-ink-50 p-4">
                <div class="flex items-center gap-2 text-ink-500">
                  <UserRound class="h-4 w-4" />
                  <p class="text-xs uppercase tracking-[0.16em]">Владелец</p>
                </div>
                <p class="mt-2 text-sm font-medium text-ink-900">{{ selectedOwnerLabel }}</p>
              </div>

              <div class="block-radius border border-ink-200 bg-ink-50 p-4">
                <p class="text-xs uppercase tracking-[0.16em] text-ink-500">Команда</p>
                <p class="mt-2 text-sm font-medium text-ink-900">{{ selectedTeamLabel }}</p>
              </div>

              <div class="block-radius border border-ink-200 bg-ink-50 p-4">
                <p class="text-xs uppercase tracking-[0.16em] text-ink-500">Период</p>
                <p class="mt-2 text-sm font-medium text-ink-900">{{ selectedQuarterLabel }}</p>
              </div>

              <div class="block-radius border border-ink-200 bg-ink-50 p-4">
                <div class="flex items-center gap-2 text-ink-500">
                  <Layers3 class="h-4 w-4" />
                  <p class="text-xs uppercase tracking-[0.16em]">Key Results</p>
                </div>
                <p class="mt-2 text-sm font-medium text-ink-900">{{ keyResults.length }} шт.</p>
              </div>
            </div>
          </div>
        </section>

        <section class="surface-muted p-5">
          <p class="text-sm font-medium text-ink-500">Перед сохранением</p>
          <p v-if="fieldError" class="mt-2 text-sm text-rose-500">
            {{ fieldError }}
          </p>
          <p v-else class="mt-2 text-sm text-ink-600">
            Проверь название цели и убедись, что у каждого KR заполнено целевое значение.
          </p>
        </section>

        <section class="surface-muted p-5">
          <p class="text-sm font-medium text-ink-500">Ответ сервера</p>
          <p v-if="submitError" class="mt-2 text-sm text-rose-500">
            {{ submitError }}
          </p>
          <p v-else class="mt-2 text-sm text-ink-600">
            После сохранения откроется карточка OKR, а прогресс KR и цели рассчитается автоматически.
          </p>
        </section>

        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
          <button
            type="button"
            class="btn btn-primary btn-lg"
            :disabled="isSubmitting"
            @click="submitForm"
          >
            <Save class="h-4 w-4" />
            {{ isSubmitting ? 'Сохраняем...' : 'Сохранить OKR' }}
          </button>

          <NuxtLink
            to="/okrs"
            class="btn btn-secondary btn-lg"
          >
            Отмена
          </NuxtLink>
        </div>
      </aside>
    </div>
  </div>
</template>
