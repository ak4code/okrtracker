<script setup lang="ts">
import { Save, X } from 'lucide-vue-next'
import type { KeyResultItem, OkrItem, KeyResultUpdatePayload } from '~/composables/useOkrApi'
import {
  normalizeFormValue,
  okrStatusOptions,
  okrStatusToApiMap,
} from '~/composables/useOkrForm'

const props = defineProps<{
  modelValue: boolean
  keyResult: KeyResultItem
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  saved: [value: OkrItem]
}>()

type FormStatus = KeyResultUpdatePayload['status']
type MetricType = KeyResultUpdatePayload['metric_type']

const okrApi = useOkrApi()
const statusOptions = okrStatusOptions as { value: FormStatus; label: string }[]
const statusToApiMap = okrStatusToApiMap as Record<KeyResultItem['status'], FormStatus>

const form = ref({
  title: '',
  description: '',
  value: '0.3',
  metricType: 'number' as MetricType,
  startValue: '0',
  currentValue: '0',
  targetValue: '0',
  status: 'draft' as FormStatus,
})

const fieldError = ref('')
const submitError = ref('')
const isSubmitting = ref(false)

const syncForm = () => {
  form.value = {
    title: props.keyResult.title,
    description: props.keyResult.description,
    value: String(props.keyResult.value),
    metricType: props.keyResult.metricType,
    startValue: String(props.keyResult.start),
    currentValue: String(props.keyResult.current),
    targetValue: String(props.keyResult.target),
    status: statusToApiMap[props.keyResult.status],
  }
  fieldError.value = ''
  submitError.value = ''
}

watch(
  () => [props.modelValue, props.keyResult.id],
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
    return 'Название KR обязательно.'
  }

  if (!normalizeFormValue(form.value.targetValue)) {
    return 'Целевое значение обязательно.'
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
    const updatedOkr = await okrApi.updateKeyResult(props.keyResult.id, {
      title: form.value.title.trim(),
      description: form.value.description.trim(),
      value: normalizeFormValue(form.value.value),
      metric_type: form.value.metricType,
      start_value: normalizeFormValue(form.value.startValue) || '0',
      current_value: normalizeFormValue(form.value.currentValue) || normalizeFormValue(form.value.startValue) || '0',
      target_value: normalizeFormValue(form.value.targetValue),
      status: form.value.status,
    })

    emit('saved', updatedOkr)
    closeModal()
  }
  catch (error: any) {
    submitError.value =
      error?.data?.detail ||
      error?.data?.title?.[0] ||
      error?.data?.metric_type?.[0] ||
      error?.data?.target_value?.[0] ||
      'Не удалось обновить key result.'
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
      <div class="surface max-h-[90vh] w-full max-w-3xl overflow-y-auto p-6 sm:p-8">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-xs uppercase tracking-[0.2em] text-ink-400">Key Result</p>
            <h2 class="mt-2 text-2xl font-semibold text-ink-900">Редактировать KR</h2>
            <p class="mt-2 text-sm text-ink-500">Измени метрику, статус и значения ключевого результата.</p>
          </div>
          <button
            class="btn btn-secondary btn-icon"
            aria-label="Закрыть модалку"
            @click="closeModal"
          >
            <X class="h-4 w-4" />
          </button>
        </div>

        <form class="mt-6 space-y-5" @submit.prevent="submitForm">
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-medium text-ink-600">Название KR</label>
              <input v-model="form.title" type="text" class="input-base" placeholder="Название ключевого результата">
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
            <label class="text-sm font-medium text-ink-600">Значение KR</label>
            <select v-model="form.value" class="input-base">
              <option value="0.3">0.3</option>
              <option value="0.7">0.7</option>
              <option value="1.0">1.0</option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium text-ink-600">Описание</label>
            <textarea v-model="form.description" rows="4" class="input-base resize-none" placeholder="Описание KR" />
          </div>

          <KeyResultMetricFields :form="form" />

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
              :disabled="isSubmitting"
            >
              <Save class="h-4 w-4" />
              {{ isSubmitting ? 'Сохраняем...' : 'Сохранить KR' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
