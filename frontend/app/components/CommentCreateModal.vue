<script setup lang="ts">
import { MessageSquareText, Save, X } from 'lucide-vue-next'
import type { OkrItem } from '~/composables/useOkrApi'

const props = defineProps<{
  modelValue: boolean
  okr: OkrItem
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  saved: [value: OkrItem]
}>()

const okrApi = useOkrApi()

const form = ref({
  text: '',
})
const fieldError = ref('')
const submitError = ref('')
const isSubmitting = ref(false)

const syncForm = () => {
  form.value = {
    text: '',
  }
  fieldError.value = ''
  submitError.value = ''
}

watch(
  () => [props.modelValue, props.okr.id],
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

const submitForm = async () => {
  fieldError.value = ''
  submitError.value = ''

  const text = form.value.text.trim()
  if (!text) {
    fieldError.value = 'Введите комментарий.'
    return
  }

  isSubmitting.value = true

  try {
    const updatedOkr = await okrApi.createComment(props.okr.id, { text })
    emit('saved', updatedOkr)
    closeModal()
  }
  catch (error: any) {
    submitError.value =
      error?.data?.text?.[0] ||
      error?.data?.detail ||
      'Не удалось сохранить комментарий.'
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
            <p class="text-xs uppercase tracking-[0.2em] text-ink-400">Комментарий</p>
            <h2 class="mt-2 text-2xl font-semibold text-ink-900">Добавить комментарий</h2>
            <p class="mt-2 text-sm text-ink-500">Зафиксируй контекст, решение или риск по цели.</p>
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
          <div class="flex items-start gap-3">
            <div class="rounded-xl bg-white p-2 text-ink-500">
              <MessageSquareText class="h-4 w-4" />
            </div>
            <div>
              <p class="text-sm font-medium text-ink-900">{{ okr.title }}</p>
              <p class="mt-1 text-sm text-ink-500">{{ okr.quarter }} · {{ okr.team }}</p>
            </div>
          </div>
        </div>

        <form class="mt-6 space-y-5" @submit.prevent="submitForm">
          <div class="space-y-2">
            <label class="text-sm font-medium text-ink-600">Текст комментария</label>
            <textarea
              v-model="form.text"
              rows="5"
              class="input-base resize-none"
              placeholder="Например: согласовали объем, обнаружили риск, перенесли срок проверки..."
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
              {{ isSubmitting ? 'Сохраняем...' : 'Сохранить комментарий' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
