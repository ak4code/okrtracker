<script setup lang="ts">
import { Save, Trash2, X } from 'lucide-vue-next'
import type { CheckInItem, OkrItem } from '~/composables/useOkrApi'

const props = defineProps<{
  modelValue: boolean
  checkIn: CheckInItem
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
const isDeleting = ref(false)
const isDeleteConfirmOpen = ref(false)

const normalizeFormValue = (value: string | number) => String(value ?? '').trim()

const syncForm = () => {
  form.value = {
    newValue: String(props.checkIn.value),
    comment: props.checkIn.note,
  }
  fieldError.value = ''
  submitError.value = ''
}

watch(
  () => [props.modelValue, props.checkIn.id],
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
  if (!normalizeFormValue(form.value.newValue)) {
    return props.checkIn.metricType === 'boolean' ? 'Новое значение обязательно.' : 'Изменение обязательно.'
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
    const updatedOkr = await okrApi.updateCheckIn(props.checkIn.id, {
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
      'Не удалось обновить check-in.'
  }
  finally {
    isSubmitting.value = false
  }
}

const deleteCurrentCheckIn = async () => {
  submitError.value = ''
  fieldError.value = ''
  isDeleting.value = true

  try {
    const updatedOkr = await okrApi.deleteCheckIn(props.checkIn.id)
    emit('saved', updatedOkr)
    closeModal()
  }
  catch (error: any) {
    submitError.value = error?.data?.detail || 'Не удалось удалить check-in.'
  }
  finally {
    isDeleting.value = false
    isDeleteConfirmOpen.value = false
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
            <h2 class="mt-2 text-2xl font-semibold text-ink-900">Редактировать check-in</h2>
            <p class="mt-2 text-sm text-ink-500">{{ checkIn.keyResultTitle || 'Обновление key result' }}</p>
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
          <div class="space-y-2">
            <label class="text-sm font-medium text-ink-600">
              {{ checkIn.metricType === 'boolean' ? 'Новое значение' : 'Изменение' }}
            </label>
            <select
              v-if="checkIn.metricType === 'boolean'"
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
              placeholder="Введите изменение"
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

          <div class="flex flex-wrap items-center justify-between gap-3 border-t border-ink-200 pt-5">
            <button type="button" class="btn btn-danger" :disabled="isDeleting || isSubmitting" @click="isDeleteConfirmOpen = true">
              <Trash2 class="h-4 w-4" />
              {{ isDeleting ? 'Удаляем...' : 'Удалить' }}
            </button>

            <div class="flex flex-wrap items-center gap-3">
              <button type="button" class="btn btn-secondary" @click="closeModal">
                Отмена
              </button>
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="isSubmitting || isDeleting"
              >
                <Save class="h-4 w-4" />
                {{ isSubmitting ? 'Сохраняем...' : 'Сохранить' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </Teleport>

  <ConfirmModal
    v-model="isDeleteConfirmOpen"
    title="Удалить check-in?"
    :description="`Это действие удалит запись обновления по ${checkIn.keyResultTitle || 'key result'} и пересчитает текущее значение KR.`"
    confirm-label="Удалить"
    :is-loading="isDeleting"
    @confirm="deleteCurrentCheckIn"
  />
</template>
