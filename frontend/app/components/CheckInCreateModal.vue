<script setup lang="ts">
import { Save, X } from 'lucide-vue-next'
import type { KeyResultItem, OkrItem } from '~/composables/useOkrApi'

const props = defineProps<{
  modelValue: boolean
  keyResult: KeyResultItem
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  saved: [value: OkrItem]
}>()

const okrApi = useOkrApi()

const form = ref({
  newValue: '0',
  comment: '',
})

const fieldError = ref('')
const submitError = ref('')
const isSubmitting = ref(false)

const syncForm = () => {
  form.value = {
    newValue: String(props.keyResult.current),
    comment: '',
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

const normalizeFormValue = (value: string | number) => String(value ?? '').trim()

const validateForm = () => {
  if (!normalizeFormValue(form.value.newValue)) {
    return 'Новое значение обязательно.'
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
    const updatedOkr = await okrApi.createCheckIn(props.keyResult.id, {
      new_value: normalizeFormValue(form.value.newValue),
      comment: form.value.comment.trim(),
    })

    emit('saved', updatedOkr)
    closeModal()
  }
  catch (error: any) {
    submitError.value =
      error?.data?.detail ||
      error?.data?.new_value?.[0] ||
      'Не удалось создать check-in.'
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
      <div class="surface max-h-[90vh] w-full max-w-2xl overflow-y-auto p-6 sm:p-8">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-xs uppercase tracking-[0.2em] text-ink-400">Check-in</p>
            <h2 class="mt-2 text-2xl font-semibold text-ink-900">Новый check-in</h2>
            <p class="mt-2 text-sm text-ink-500">Зафиксируй обновление по ключевому результату.</p>
          </div>
          <button
            class="btn btn-secondary btn-icon"
            aria-label="Закрыть модалку"
            @click="closeModal"
          >
            <X class="h-4 w-4" />
          </button>
        </div>

        <div class="mt-6 block-radius border border-ink-200 bg-ink-50/70 p-4">
          <p class="text-sm font-medium text-ink-900">{{ keyResult.title }}</p>
          <p class="mt-1 text-sm text-ink-500">Текущее значение: {{ keyResult.current }} {{ keyResult.unit }}</p>
          <p class="mt-1 text-sm text-ink-500">Цель: {{ keyResult.target }} {{ keyResult.unit }}</p>
        </div>

        <form class="mt-6 space-y-5" @submit.prevent="submitForm">
          <div class="space-y-2">
            <label class="text-sm font-medium text-ink-600">
              Текущее значение
            </label>
            <select
              v-if="keyResult.metricType === 'boolean'"
              v-model="form.newValue"
              class="input-base"
            >
              <option value="0">Нет</option>
              <option value="1">Да</option>
            </select>
            <input
              v-else
              v-model="form.newValue"
              type="number"
              step="0.01"
              class="input-base"
              placeholder="Например 10, 45 или 80"
            >
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium text-ink-600">Комментарий</label>
            <textarea
              v-model="form.comment"
              rows="4"
              class="input-base resize-none"
              placeholder="Что изменилось и почему?"
            />
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
              :disabled="isSubmitting"
            >
              <Save class="h-4 w-4" />
              {{ isSubmitting ? 'Сохраняем...' : 'Создать check-in' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
