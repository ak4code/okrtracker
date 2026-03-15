<script setup lang="ts">
import { Save, X } from 'lucide-vue-next'
import type { OkrItem, OkrUpdatePayload } from '~/composables/useOkrApi'
import { okrStatusOptions, okrStatusToApiMap } from '~/composables/useOkrForm'

const props = defineProps<{
  modelValue: boolean
  okr: OkrItem
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  saved: [value: OkrItem]
}>()

type FormStatus = OkrUpdatePayload['status']

const okrApi = useOkrApi()

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

const { users, teams, quarters, isLoading } = await useOkrLookups('okr-edit')

const statusOptions = okrStatusOptions as { value: FormStatus; label: string }[]
const statusToApiMap = okrStatusToApiMap as Record<OkrItem['status'], FormStatus>

const syncForm = () => {
  form.value = {
    title: props.okr.title,
    description: props.okr.description,
    ownerId: String(props.okr.ownerId),
    teamId: String(props.okr.teamId),
    periodId: String(props.okr.periodId),
    status: statusToApiMap[props.okr.status],
  }
  fieldError.value = ''
  submitError.value = ''
}

watch(
  () => [props.modelValue, props.okr.id, props.okr.updatedAt],
  ([isOpen]) => {
    if (isOpen) {
      syncForm()
    }
  },
  { immediate: true },
)

const closeModal = () => {
  emit('update:modelValue', false)
}

const validateForm = () => {
  if (!form.value.title.trim()) {
    return 'Название цели обязательно.'
  }

  if (!form.value.ownerId || !form.value.teamId || !form.value.periodId) {
    return 'Выбери владельца, команду и квартал.'
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
    const updatedOkr = await okrApi.updateOkr(props.okr.id, {
      title: form.value.title.trim(),
      description: form.value.description.trim(),
      owner_id: Number(form.value.ownerId),
      team_id: Number(form.value.teamId),
      period_id: Number(form.value.periodId),
      status: form.value.status,
    })

    emit('saved', updatedOkr)
    closeModal()
  }
  catch (error: any) {
    submitError.value =
      error?.data?.detail ||
      error?.data?.non_field_errors?.[0] ||
      error?.data?.title?.[0] ||
      error?.data?.owner_id?.[0] ||
      error?.data?.team_id?.[0] ||
      error?.data?.period_id?.[0] ||
      error?.data?.status?.[0] ||
      'Не удалось обновить OKR.'
  }
  finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center bg-ink-900/55 px-4 py-8 backdrop-blur-sm"
      @click.self="closeModal"
    >
      <div class="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-[28px] border border-ink-200 bg-white p-6 shadow-2xl sm:p-8">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-xs uppercase tracking-[0.2em] text-ink-400">Редактирование</p>
            <h2 class="mt-2 text-2xl font-semibold text-ink-900">Изменить OKR</h2>
            <p class="mt-2 text-sm text-ink-500">Обновляются основные поля цели. Key results редактируются отдельно.</p>
          </div>
          <button
            class="btn btn-secondary btn-icon"
            aria-label="Закрыть модалку"
            @click="closeModal"
          >
            <X class="h-4 w-4" />
          </button>
        </div>

        <div v-if="isLoading" class="mt-6 block-radius border border-ink-200 bg-ink-50 px-4 py-6 text-sm text-ink-500">
          Загружаем справочники формы...
        </div>

        <form v-else class="mt-6 space-y-5" @submit.prevent="submitForm">
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-medium text-ink-600">Название цели</label>
              <input v-model="form.title" type="text" class="input-base" placeholder="Название OKR">
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium text-ink-600">Статус</label>
              <select v-model="form.status" class="input-base">
                <option v-for="item in statusOptions" :key="item.value" :value="item.value">
                  {{ item.label }}
                </option>
              </select>
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium text-ink-600">Описание</label>
            <textarea
              v-model="form.description"
              rows="5"
              class="input-base resize-none"
              placeholder="Кратко опиши цель и ожидаемый эффект."
            />
          </div>

          <div class="grid gap-4 md:grid-cols-3">
            <div class="space-y-2">
              <label class="text-sm font-medium text-ink-600">Владелец</label>
              <select v-model="form.ownerId" class="input-base">
                <option v-for="item in users" :key="item.id" :value="String(item.id)">
                  {{ item.firstName || item.lastName ? `${item.firstName} ${item.lastName}`.trim() : item.email }}
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

          <div v-if="fieldError" class="block-radius border border-amber-200 bg-amber-100/60 px-4 py-3 text-sm text-amber-500">
            {{ fieldError }}
          </div>

          <div v-if="submitError" class="block-radius border border-rose-200 bg-rose-100/60 px-4 py-3 text-sm text-rose-500">
            {{ submitError }}
          </div>

          <div class="flex flex-wrap items-center justify-end gap-3 border-t border-ink-200 pt-5">
            <button type="button" class="btn btn-secondary" @click="closeModal">
              Отмена
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isSubmitting || isLoading"
            >
              <Save class="h-4 w-4" />
              {{ isSubmitting ? 'Сохраняем...' : 'Сохранить OKR' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
